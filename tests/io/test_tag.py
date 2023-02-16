from io import BytesIO

from pytest import mark

from pure_protobuf.io.tag import Tag
from pure_protobuf.io.wire_type import WireType
from tests import pytest_test_id


@mark.parametrize(
    ("buffer", "expected"),
    [
        (b"\x08", Tag(field_number=1, wire_type=WireType.VARINT)),
    ],
    ids=pytest_test_id,
)
def test_read_from(buffer: bytes, expected: Tag) -> None:
    assert Tag.read_from(BytesIO(buffer)) == expected
