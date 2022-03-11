"""
`pure-protobuf` contributors © 2011-2019
"""

import functools
from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, Callable, Iterable, Tuple

from pure_protobuf.enums import WireType
from pure_protobuf.io_ import IO, Dumps
from pure_protobuf.oneof import OneOf_, OneOfPartInfo, scheme
from pure_protobuf.serializers import Serializer, bytes_serializer, unsigned_varint_serializer


# TODO: perhaps it's good to add a type parameter:
# TODO: https://docs.python.org/3/library/typing.html#user-defined-generic-types
class Field(Dumps, ABC):
    def __init__(self, number: int, name: str, serializer: Serializer):
        self.number = number
        self.name = name
        self.serializer = serializer
        self.wire_type = serializer.wire_type

    @abstractmethod
    def validate(self, value: Any):
        """
        Validates a value. Raises an exception in case of an error.
        """
        raise NotImplementedError()

    @abstractmethod
    def dump(self, value: Any, io: IO):
        """
        Serializes a value into a file-like object.
        """
        raise NotImplementedError()

    def dump_key(self, io: IO):
        """
        Serializes field key: number and wire type.
        """
        unsigned_varint_serializer.dump((self.number << 3) | self.wire_type, io)

    @abstractmethod
    def load(self, wire_type: WireType, io: IO) -> Any:
        """
        Deserializes a field value from a file-like object.
        Accepts received wire type.
        """
        raise NotImplementedError()

    @abstractmethod
    def merge(self, old_value: Any, new_value: Any) -> Any:
        """
        Merge existing value with a new value received from an input stream.
        """
        raise NotImplementedError()


class NonRepeatedField(Field):
    """
    Handles non-repeated field.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#scalar
    See also: https://developers.google.com/protocol-buffers/docs/encoding#optional
    """

    def __init__(self, number: int, name: str, serializer: Serializer, is_optional: bool):
        super().__init__(number, name, serializer)
        self.is_optional = is_optional

    def validate(self, value: Any):
        if value is not None or not self.is_optional:
            self.serializer.validate(value)

    def dump(self, value: Any, io: IO):
        if value is not None:
            self.dump_key(io)
            self.serializer.dump(value, io)

    def load(self, wire_type: WireType, io: IO) -> Any:
        if wire_type != self.serializer.wire_type:
            raise ValueError(f'expected {self.serializer.wire_type}, got {wire_type}')
        return self.serializer.load(io)

    def merge(self, old_value: Any, new_value: Any) -> Any:
        return self.serializer.merge(old_value, new_value)


class RepeatedField(Field, ABC):
    """
    Handles repeated and packed repeated field.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#optional
    """

    def validate(self, value: Any):
        for item in value:
            self.serializer.validate(item)

    def load(self, wire_type: WireType, io: IO) -> Any:
        if self.serializer.wire_type != WireType.BYTES and wire_type == WireType.BYTES:
            # Protocol buffer parsers must be able to parse repeated fields
            # that were compiled as packed as if they were not packed, and vice versa.
            # See also: https://developers.google.com/protocol-buffers/docs/encoding#packed
            return list(self.load_packed(bytes_serializer.load(io)))
        if wire_type == self.serializer.wire_type:
            return [self.serializer.load(io)]
        raise ValueError((f'expected {self.serializer.wire_type} \n'
                          'or {WireType.BYTES}, got {wire_type}'))

    def load_packed(self, bytes_: bytes) -> Iterable[Any]:
        """
        Deserializes repeated values from a packed byte string.
        """
        with BytesIO(bytes_) as io:
            while io.tell() < len(bytes_):
                yield self.serializer.load(io)

    def merge(self, old_value: Any, new_value: Any) -> Any:
        if old_value is not None:
            return [*old_value, *new_value]
        return new_value


class UnpackedRepeatedField(RepeatedField):
    """
    See also: https://developers.google.com/protocol-buffers/docs/encoding#optional
    """

    def dump(self, value: Any, io: IO):
        for item in value:
            self.dump_key(io)
            self.serializer.dump(item, io)


class PackedRepeatedField(RepeatedField):
    """
    Dumps repeated value as a byte string.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#packed
    """

    def __init__(self, number: int, name: str, serializer: Serializer):
        super().__init__(number, name, serializer)
        self.wire_type = WireType.BYTES

    def dump(self, value: Any, io: IO):
        with BytesIO() as inner_io:
            for item in value:
                self.serializer.dump(item, inner_io)
            self.dump_key(io)
            bytes_serializer.dump(inner_io.getvalue(), io)


class OneOfPartField(Field):
    def __init__(self, number: int, name: str,
                 scheme_: Tuple[OneOfPartInfo, ...], origin: Field):
        super().__init__(number, name, origin.serializer)

        self.scheme = scheme_
        self.origin: Field = origin

    def do_if_current_set(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore
        @functools.wraps(func)
        def inner(self, value, *args) -> Any:
            if not isinstance(value, OneOf_):
                return func(self, value, *args)

            # Further checks matter only if passed OneOf_ is from the same class
            # as this field and if set field of passed OneOf_ is same as name
            # of saved origin Field.
            #
            # Tricky scheme refs comparison, but seems to work.
            #
            # value: OneOf_
            which_set = value.which_one_of
            if self.scheme != scheme(value) or which_set != self.origin.name:
                return None

            original_value = getattr(value, which_set)
            return func(self, original_value, *args)

        return inner

    @do_if_current_set
    def validate(self, value: OneOf_):
        self.origin.validate(value)

    @do_if_current_set
    def dump(self, value: OneOf_, io: IO):
        self.origin.dump(value, io)

    def merge(self, old_value: OneOf_, new_value: OneOf_) -> Any:
        return new_value

    def load(self, wire_type: WireType, io: IO) -> Any:
        val = OneOf_(self.scheme)
        setattr(val, self.origin.name, self.origin.load(wire_type, io))
        return val
