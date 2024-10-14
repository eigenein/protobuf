from collections.abc import ByteString
from typing import Annotated, Any, Optional

from pytest import mark, raises

from pure_protobuf.annotations import Field, uint
from pure_protobuf.descriptors._field import _FieldDescriptor
from pure_protobuf.exceptions import IncorrectAnnotationError
from pure_protobuf.io.wrappers import to_bytes
from pure_protobuf.message import BaseMessage
from tests import pytest_test_id
from tests.definitions import ExampleEnum, RecursiveMessage


@mark.parametrize("hint", [int, Annotated[int, ...]])
def test_from_attribute_ignored(hint: Any) -> None:
    """Test ignored type hints."""
    assert _FieldDescriptor.from_attribute(BaseMessage, hint) is None


@mark.parametrize(
    "hint",
    [
        Annotated[int, Field(0)],
        Annotated[int, Field(19000)],
    ],
)
def test_from_inner_hint_incorrect(hint: Any) -> None:
    with raises(IncorrectAnnotationError):
        _FieldDescriptor.from_attribute(BaseMessage, hint)


@mark.parametrize(
    ("hint", "value", "expected"),
    [
        (Annotated[int, Field(1)], 150, b"\x08\x96\x01"),
        (Annotated[uint, Field(1)], 150, b"\x08\x96\x01"),
        (Annotated[list[int], Field(1)], [1, 150, 2], b"\x0a\x04\x01\x96\x01\x02"),
        (Annotated[list[bytes], Field(1)], [b"B", b"C"], b"\x0a\x01B\x0a\x01C"),
        (Annotated[Optional[bytes], Field(1)], None, b""),
        (Annotated[ByteString, Field(1)], b"Testing", b"\x0a\x07Testing"),
        (Annotated[ExampleEnum, Field(1)], ExampleEnum.BAR, b"\x08\x02"),
        (
            Annotated[RecursiveMessage, Field(42)],
            RecursiveMessage(payload=1, inner=RecursiveMessage(payload=2)),
            b"\xd2\x02\x06\x08\x01\x12\x02\x08\x02",
        ),
        (Annotated[list[int], Field(1, packed=False)], [1, 2], b"\x08\x01\x08\x02"),
        (Annotated[int, Field(1)], -2, b"\x08\xfe\xff\xff\xff\xff\xff\xff\xff\xff\x01"),
        # TODO: cyclic dependencies, https://github.com/eigenein/protobuf/issues/108.
    ],
    ids=pytest_test_id,
)
def test_field_descriptor_write(hint: Any, value: Any, expected: bytes) -> None:
    """Test writes with `Annotated` hints."""
    descriptor = _FieldDescriptor.from_attribute(BaseMessage, hint)
    assert descriptor is not None
    assert to_bytes(descriptor.write, value) == expected
