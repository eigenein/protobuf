from enum import IntEnum
from io import BytesIO

from pytest import mark, raises
from pytest_benchmark.fixture import BenchmarkFixture

from pure_protobuf.exceptions import IncorrectValueError
from pure_protobuf.io.varint import (
    ReadEnum,
    WriteEnum,
    read_signed_varint,
    read_unsigned_varint,
    write_signed_varint,
    write_unsigned_varint,
)
from pure_protobuf.io.wrappers import to_bytes
from tests import pytest_test_id
from tests.definitions import ExampleEnum

UVARINT_CASES = [
    (0, b"\x00"),
    (3, b"\x03"),
    (270, b"\x8E\x02"),
    (86942, b"\x9E\xA7\x05"),
]


@mark.parametrize("value, bytes_", UVARINT_CASES, ids=pytest_test_id)
def test_write_unsigned_varint(value: int, bytes_: bytes, benchmark: BenchmarkFixture):
    assert benchmark(to_bytes, write_unsigned_varint, value) == bytes_


@mark.parametrize("value, bytes_", UVARINT_CASES, ids=pytest_test_id)
def test_read_unsigned_varint(value: int, bytes_: bytes, benchmark: BenchmarkFixture, bytes_io):
    assert benchmark.pedantic(read_unsigned_varint, setup=bytes_io(bytes_)) == value


SIGNED_VARINT_TESTS = [
    (0, b"\x00"),
    (-1, b"\x01"),
    (1, b"\x02"),
    (-2, b"\x03"),
]


@mark.parametrize("value, bytes_", SIGNED_VARINT_TESTS, ids=pytest_test_id)
def test_signed_varint_serializer_dumps(value: int, bytes_: bytes, benchmark):
    assert benchmark(to_bytes, write_signed_varint, value) == bytes_


@mark.parametrize("value, bytes_", SIGNED_VARINT_TESTS, ids=pytest_test_id)
def test_signed_varint_serializer_loads(value: int, bytes_: bytes, benchmark, bytes_io):
    assert benchmark.pedantic(read_signed_varint, setup=bytes_io(bytes_)) == value


ENUM_CASES = [
    (ExampleEnum.FOO, b"\x01"),
    (ExampleEnum.BAR, b"\x02"),
]


@mark.parametrize("value, bytes_", ENUM_CASES)
def test_read_enum(value: IntEnum, bytes_: bytes):
    assert next(ReadEnum(ExampleEnum)(BytesIO(bytes_))) == value


@mark.parametrize("bytes_", [b"\x03"])
def test_read_enum_error(bytes_: bytes):
    with raises(IncorrectValueError):
        next(ReadEnum(ExampleEnum)(BytesIO(bytes_)))


@mark.parametrize("value, bytes_", ENUM_CASES)
def test_write_enum(value: ExampleEnum, bytes_: bytes):
    assert to_bytes(WriteEnum[ExampleEnum](), value) == bytes_
