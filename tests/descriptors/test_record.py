from io import BytesIO
from typing import Any, Tuple
from urllib.parse import ParseResult

from pytest import mark, raises

from pure_protobuf.descriptors.record import (
    FLOAT_DESCRIPTOR,
    URL_DESCRIPTOR,
    RecordDescriptor,
)
from pure_protobuf.exceptions import UnsupportedAnnotationError
from pure_protobuf.io.wire_type import WireType
from pure_protobuf.io.wrappers import to_bytes
from pure_protobuf.message import BaseMessage


@mark.parametrize(
    "inner_hint",
    [
        Tuple[int, str],
    ],
)
def test_from_inner_hint_unsupported(inner_hint: Any):
    with raises(UnsupportedAnnotationError):
        RecordDescriptor.from_inner_type_hint(BaseMessage, inner_hint)


@mark.parametrize(
    "value, encoded",
    [
        (0.0, b"\x00\x00\x00\x00"),
        (1.0, b"\x00\x00\x80\x3F"),
    ],
)
def test_struct(value: float, encoded: bytes):
    assert to_bytes(FLOAT_DESCRIPTOR.write, value) == encoded
    assert next(FLOAT_DESCRIPTOR.read(BytesIO(encoded), WireType.I32)) == value


# noinspection PyArgumentList
@mark.parametrize(
    "url, encoded",
    [
        (
            ParseResult(
                scheme="https",
                netloc="example.com",
                path="",
                params="",
                query="",
                fragment="",
            ),
            b"\x13https://example.com",
        ),
    ],
)
def test_url(url: ParseResult, encoded: bytes):
    assert to_bytes(URL_DESCRIPTOR.write, url) == encoded
    assert next(URL_DESCRIPTOR.read(BytesIO(encoded), WireType.LEN)) == url
