"""Reading and writing parsed URLs."""

from typing import IO, Iterator
from urllib.parse import ParseResult, urlparse, urlunparse

from pure_protobuf.interfaces.read import Read
from pure_protobuf.interfaces.write import Write
from pure_protobuf.io.bytes_ import read_string, write_string


class ReadUrl(Read[ParseResult]):
    __slots__ = ()

    def __call__(self, io: IO[bytes]) -> Iterator[ParseResult]:
        yield urlparse(read_string(io))


class WriteUrl(Write[ParseResult]):
    __slots__ = ()

    def __call__(self, value: ParseResult, io: IO[bytes]) -> None:
        write_string(urlunparse(value), io)
