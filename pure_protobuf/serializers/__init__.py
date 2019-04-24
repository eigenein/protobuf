"""
Serializers for the dataclasses interface.

`pure-protobuf` contributors © 2011-2019
"""

import struct
from abc import ABC
from enum import IntEnum
from itertools import count
from struct import pack, unpack
from typing import Any, Type

from pure_protobuf import types
from pure_protobuf.enums import WireType
from pure_protobuf.io_ import IO, Dumps, Loads


# TODO: add type argument, see also https://github.com/eigenein/protobuf/issues/27
class Serializer(Dumps, Loads, ABC):
    # Default wire type for a value.
    # May be overridden by a wrapping serializer.
    wire_type: WireType

    def validate(self, value: Any):
        """
        Validates the value. Raises an exception if value incorrect.
        """

    def merge(self, old_value: Any, new_value: Any) -> Any:
        """
        Merges two unrepeated values on a wire.
        """
        return new_value


class UnsignedVarintSerializer(Serializer):
    """
    Serializes a generic base-128 unsigned varint.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#varints
    See also: https://en.wikipedia.org/wiki/LEB128
    """

    wire_type = WireType.VARINT

    def validate(self, value: Any):
        if not isinstance(value, int) or value < 0:
            raise ValueError('a non-negative integer is expected')

    def dump(self, value: Any, io: IO):
        write_varint(value, io)

    def load(self, io: IO) -> Any:
        return read_varint(io)


unsigned_varint_serializer = UnsignedVarintSerializer()


class SignedVarintSerializer(Serializer):
    """
    Serializes a generic base-128 signed varint.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#signed-integers
    """

    wire_type = unsigned_varint_serializer.wire_type

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError('an integer is expected')

    def dump(self, value: Any, io: IO):
        return unsigned_varint_serializer.dump(abs(value) * 2 - (value < 0), io)

    def load(self, io: IO) -> Any:
        # See also: https://stackoverflow.com/a/2211086/359730
        n = unsigned_varint_serializer.load(io)
        return (n >> 1) ^ (-(n & 1))


signed_varint_serializer = SignedVarintSerializer()


class BytesSerializer(Serializer):
    """
    Serializes a byte string.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#strings
    """

    wire_type = WireType.BYTES

    def validate(self, value: Any):
        try:
            memoryview(value)
        except TypeError:
            raise ValueError(f'a bytes-like object is required, not `{type(value)}`')

    def dump(self, value: Any, io: IO):
        unsigned_varint_serializer.dump(len(value), io)
        io.write(value)

    def load(self, io: IO) -> Any:
        length = unsigned_varint_serializer.load(io)
        return io.read(length)


bytes_serializer = BytesSerializer()


class StringSerializer(Serializer):
    """
    Serializes a UTF8-encoded string.
    """

    wire_type = bytes_serializer.wire_type

    def validate(self, value: Any):
        if not isinstance(value, str):
            raise ValueError('a string is expected')

    def dump(self, value: Any, io: IO):
        bytes_serializer.dump(value.encode('utf-8'), io)

    def load(self, io: IO) -> Any:
        return bytes_serializer.load(io).decode('utf-8')


class UnsignedInt32Serializer(Serializer):
    """
    Serializes 32-bit unsigned varint.
    """

    wire_type = unsigned_varint_serializer.wire_type

    def validate(self, value: Any):
        unsigned_varint_serializer.validate(value)
        if not 0 <= value <= 0xFFFFFFFF:
            raise ValueError(f'value is out of 32-bit unsigned integer range')

    def dump(self, value: Any, io: IO):
        unsigned_varint_serializer.dump(value, io)

    def load(self, io: IO) -> Any:
        return unsigned_varint_serializer.load(io)


class UnsignedInt64Serializer(Serializer):
    """
    Serializes 64-bit unsigned varint.
    """

    wire_type = unsigned_varint_serializer.wire_type

    def validate(self, value: Any):
        unsigned_varint_serializer.validate(value)
        if not 0 <= value <= 0xFFFFFFFF_FFFFFFFF:
            raise ValueError(f'value is out of 64-bit unsigned integer range')

    def dump(self, value: Any, io: IO):
        unsigned_varint_serializer.dump(value, io)

    def load(self, io: IO) -> Any:
        return unsigned_varint_serializer.load(io)


class SignedInt32Serializer(Serializer):
    """
    Serializes 32-bit signed varint.
    """

    wire_type = signed_varint_serializer.wire_type

    def validate(self, value: Any):
        signed_varint_serializer.validate(value)
        if not -0x7FFFFFFF <= value <= 0x7FFFFFFF:
            raise ValueError(f'value is out of 32-bit signed integer range')

    def dump(self, value: Any, io: IO):
        signed_varint_serializer.dump(value, io)

    def load(self, io: IO) -> Any:
        return signed_varint_serializer.load(io)


class SignedInt64Serializer(Serializer):
    """
    Serializes 64-bit signed varint.
    """

    wire_type = signed_varint_serializer.wire_type

    def validate(self, value: Any):
        signed_varint_serializer.validate(value)
        if not -0x7FFFFFFF_FFFFFFFF <= value <= 0x7FFFFFFF_FFFFFFFF:
            raise ValueError(f'value is out of 64-bit signed integer range')

    def dump(self, value: Any, io: IO):
        signed_varint_serializer.dump(value, io)

    def load(self, io: IO) -> Any:
        return signed_varint_serializer.load(io)


class BooleanSerializer(Serializer):
    """
    Serializes a boolean value.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#scalar
    """

    wire_type = WireType.VARINT

    def validate(self, value: Any):
        if not isinstance(value, bool):
            raise ValueError('a boolean is expected')

    def dump(self, value: Any, io: IO):
        io.write(b'\x01' if value else b'\x00')

    def load(self, io: IO) -> Any:
        return bool(unsigned_varint_serializer.load(io))


class SignedFixed32Serializer(Serializer):
    """
    Serializes 32-bit signed integer.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError('an integer is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<i', value))

    def load(self, io: IO) -> Any:
        return unpack('<i', io.read(4))[0]


class UnsignedFixed32Serializer(Serializer):
    """
    Serializes 32-bit unsigned integer.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError('an integer is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<I', value))

    def load(self, io: IO) -> Any:
        return unpack('<I', io.read(4))[0]


class SignedFixed64Serializer(Serializer):
    """
    Serializes 64-bit signed integer.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG_LONG

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError('an integer is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<q', value))

    def load(self, io: IO) -> Any:
        return unpack('<q', io.read(8))[0]


class UnsignedFixed64Serializer(Serializer):
    """
    Serializes 64-bit unsigned integer.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG_LONG

    def validate(self, value: Any):
        if not isinstance(value, int):
            raise ValueError('an integer is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<Q', value))

    def load(self, io: IO) -> Any:
        return unpack('<Q', io.read(8))[0]


class FloatSerializer(Serializer):
    """
    Serializes 32-bit floating-point value.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG

    def validate(self, value: Any):
        if not isinstance(value, float):
            raise ValueError('a floating-point value is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<f', value))

    def load(self, io: IO) -> Any:
        return unpack('<f', io.read(4))[0]


class DoubleSerializer(Serializer):
    """
    Serializes 64-bit double floating-point value.
    See also: https://developers.google.com/protocol-buffers/docs/encoding#non-varint-numbers
    """

    wire_type = WireType.LONG_LONG

    def validate(self, value: Any):
        if not isinstance(value, float):
            raise ValueError('a floating-point value is expected')

    def dump(self, value: Any, io: IO):
        io.write(pack('<d', value))

    def load(self, io: IO) -> Any:
        return unpack('<d', io.read(8))[0]


class IntEnumSerializer(Serializer):
    """
    Serializes integer enumeration value.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#enum
    """

    wire_type = WireType.VARINT

    def __init__(self, type_: Type[IntEnum]):
        self.type_ = type_

    def validate(self, value: Any):
        if not isinstance(value, self.type_):
            raise ValueError(f'{self.type_} instance is expected, got {type(value)}')

    def dump(self, value: Any, io: IO):
        unsigned_varint_serializer.dump(value, io)

    def load(self, io: IO):
        return self.type_(unsigned_varint_serializer.load(io))


class MessageSerializer(Serializer):
    """
    Serializes an entire message.
    """

    wire_type = WireType.BYTES

    def __init__(self, type_: Any):
        self.type_ = type_

    def validate(self, value: Any):
        if not isinstance(value, self.type_):
            raise ValueError(f'{self.type_} is expected, but got {type(value)}')
        for field_ in value.__protobuf_fields__.values():
            field_.validate(getattr(value, field_.name))

    def dump(self, value: Any, io: IO):
        for number, field_ in value.__protobuf_fields__.items():
            field_value = getattr(value, field_.name)
            try:
                field_.dump(field_value, io)
            except (ValueError, struct.error) as e:
                raise ValueError(f'field `{field_.name}`: {e}, got `{field_value}`') from e

    def load(self, io: IO) -> Any:
        values = {}
        while True:
            try:
                key = unsigned_varint_serializer.load(io)
            except ValueError:
                break
            wire_type = WireType(key & 0b111)
            field = self.type_.__protobuf_fields__.get(key >> 3)
            if field is not None:
                old_value = values.get(field.name)
                new_value = field.load(wire_type, io)
                values[field.name] = field.merge(old_value, new_value)
            else:
                SKIP[wire_type](io)
        return self.type_(**values)

    def merge(self, old_value: Any, new_value: Any) -> Any:
        # For embedded message fields, the parser merges multiple instances of the same field,
        # as if with the ``Message::MergeFrom`` method.
        # See also: https://developers.google.com/protocol-buffers/docs/encoding#optional
        if old_value is not None:
            old_value.merge_from(new_value)
            return old_value
        else:
            return new_value


class PackingSerializer(Serializer):
    """
    Wraps an inner serializer into a byte string serializer.
    """

    wire_type = bytes_serializer.wire_type

    def __init__(self, inner: Serializer):
        self.inner = inner

    def validate(self, value: Any):
        self.inner.validate(value)

    def dump(self, value: Any, io: IO):
        bytes_serializer.dump(self.inner.dumps(value), io)

    def load(self, io: IO) -> Any:
        return self.inner.loads(bytes_serializer.load(io))

    def merge(self, old_value: Any, new_value: Any) -> Any:
        return self.inner.merge(old_value, new_value)


def read_varint(io: IO) -> types.uint:
    """
    Read unsigned `VarInt` from a file-like object.
    """
    value = 0
    for shift in count(0, 7):
        byte, = io.read(1)
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value


def write_varint(value: types.uint, io: IO):
    """
    Write unsigned `VarInt` to a file-like object.
    """
    while value > 0x7F:
        io.write(bytes((value & 0x7F | 0x80,)))
        value >>= 7
    io.write(bytes((value,)))


def skip_varint(io: IO):
    while io.read(1)[0] & 0x80:
        pass


def skip_fixed_32(io: IO):
    io.read(4)


def skip_fixed_64(io: IO):
    io.read(8)


def skip_bytes(io: IO):
    io.read(unsigned_varint_serializer.load(io))


# Functions to skip unknown field values.
SKIP = {
    WireType.BYTES: skip_bytes,
    WireType.LONG: skip_fixed_32,
    WireType.LONG_LONG: skip_fixed_64,
    WireType.VARINT: skip_varint,
}
