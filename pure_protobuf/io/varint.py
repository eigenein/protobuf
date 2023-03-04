"""
Reading and writing varints and the derivative types.

See Also:
    - https://developers.google.com/protocol-buffers/docs/encoding#varints
"""

from enum import IntEnum
from itertools import count
from sys import byteorder
from typing import IO, Generic, Iterator, Type, TypeVar, cast

from pure_protobuf.annotations import int32, int64, uint
from pure_protobuf.exceptions import IncorrectValueError
from pure_protobuf.helpers.io import read_byte_checked
from pure_protobuf.interfaces._skip import Skip
from pure_protobuf.interfaces.read import Read, ReadSingular
from pure_protobuf.interfaces.write import Write


class SkipVarint(Skip):
    def __call__(self, io: IO[bytes]) -> None:
        while read_byte_checked(io) & 0x80:
            pass


class ReadUnsignedVarint(ReadSingular[uint]):
    """Reads unsigned varint from the stream."""

    def __call__(self, io: IO[bytes]) -> uint:
        value = 0
        for shift in count(0, 7):
            byte = read_byte_checked(io)
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return uint(value)
        raise AssertionError("unreachable code")


class WriteUnsignedVarint(Write[uint]):
    """Writes unsigned varint to the stream."""

    def __call__(self, value: uint, io: IO[bytes]) -> None:
        value = int(value)
        while value > 0x7F:
            io.write(bytes((value & 0x7F | 0x80,)))
            value >>= 7
        io.write(bytes((value,)))


skip_varint = SkipVarint()
read_unsigned_varint = ReadUnsignedVarint()
write_unsigned_varint = WriteUnsignedVarint()


class ReadSignedVarint(ReadSingular[int]):
    """
    Reads a **signed** varint.

    See Also:
        - https://stackoverflow.com/a/2211086/359730.
    """

    def __call__(self, io: IO[bytes]) -> int:
        value = read_unsigned_varint(io)
        return (value >> 1) ^ (-(value & 1))


class WriteSignedVarint(Write[int]):
    """Writes a **signed** varint."""

    def __call__(self, value: int, io: IO[bytes]) -> None:
        write_unsigned_varint(uint(abs(value) * 2 - (value < 0)), io)


read_signed_varint = ReadSignedVarint()
write_signed_varint = WriteSignedVarint()


TwosComplimentIntegerT = TypeVar("TwosComplimentIntegerT", int32, int64, int)


class ReadTwosComplimentVarint(Generic[TwosComplimentIntegerT], ReadSingular[TwosComplimentIntegerT]):
    """
    Reads a two's compliment varint.

    See Also:
        - https://protobuf.dev/programming-guides/encoding/#signed-ints
    """

    def __call__(self, io: IO[bytes]) -> TwosComplimentIntegerT:
        varint = read_unsigned_varint(io)
        return cast(
            TwosComplimentIntegerT,
            int.from_bytes(
                varint.to_bytes(8, byteorder, signed=False),
                byteorder,
                signed=True,
            ),
        )


class WriteTwosComplimentVarint(Generic[TwosComplimentIntegerT], Write[TwosComplimentIntegerT]):
    """
    Writes a two's compliment varint.

    See Also:
        - https://protobuf.dev/programming-guides/encoding/#signed-ints
    """

    def __call__(self, value: TwosComplimentIntegerT, io: IO[bytes]) -> None:
        compliment = int.from_bytes(
            value.to_bytes(8, byteorder, signed=True),
            byteorder,
            signed=False,
        )
        return write_unsigned_varint(uint(compliment), io)


class ReadBool(ReadSingular[bool]):
    def __call__(self, io: IO[bytes]) -> bool:
        return bool(read_unsigned_varint(io))


class WriteBool(Write[bool]):
    def __call__(self, value: bool, io: IO[bytes]) -> None:
        write_unsigned_varint(uint(value), io)


read_bool = ReadBool()
write_bool = WriteBool()


EnumT = TypeVar("EnumT", bound=IntEnum)


class ReadEnum(Read[EnumT]):
    __slots__ = ("enum_type",)

    # noinspection PyProtocol
    def __init__(self, enum_type: Type[EnumT]) -> None:
        self.enum_type = enum_type

    def __call__(self, io: IO[bytes]) -> Iterator[EnumT]:
        value = read_unsigned_varint(io)
        try:
            yield self.enum_type(value)
        except ValueError as e:
            raise IncorrectValueError(
                f"incorrect value {value} for enum `{self.enum_type!r}`",
            ) from e

    def __repr__(self) -> str:  # noqa: D105
        return f"{type(self).__name__}({self.enum_type.__name__})"


class WriteEnum(Write[EnumT]):
    __slots__ = ()

    def __call__(self, value: EnumT, io: IO[bytes]) -> None:
        # noinspection PyTypeChecker
        write_unsigned_varint(uint(value.value), io)
