from pytest import mark
from pytest_benchmark.fixture import BenchmarkFixture

from pure_protobuf.io.bytes_ import read_bytes, read_string, write_bytes, write_string
from pure_protobuf.io.wrappers import to_bytes

BYTES_CASES = [
    (b"testing", b"\x07testing"),
    (bytearray(b"testing"), b"\x07testing"),
    (memoryview(b"testing"), b"\x07testing"),
]


@mark.parametrize("value, bytes_", BYTES_CASES)
def test_write_bytes(value: bytes, bytes_: bytes, benchmark: BenchmarkFixture):
    assert benchmark(to_bytes, write_bytes, value) == bytes_


@mark.parametrize("value, bytes_", BYTES_CASES)
def test_read_bytes(value: bytes, bytes_: bytes, benchmark: BenchmarkFixture, bytes_io):
    assert benchmark.pedantic(read_bytes, setup=bytes_io(bytes_)) == value


STRING_CASES = [
    ("Привет", b"\x0c\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82"),
]


@mark.parametrize("value, bytes_", STRING_CASES)
def test_write_string(value: str, bytes_: bytes, benchmark: BenchmarkFixture):
    assert benchmark(to_bytes, write_string, value) == bytes_


@mark.parametrize("value, bytes_", STRING_CASES)
def test_read_string(value: str, bytes_: bytes, benchmark: BenchmarkFixture, bytes_io):
    assert benchmark.pedantic(read_string, setup=bytes_io(bytes_)) == value
