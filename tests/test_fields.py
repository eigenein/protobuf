"""
`pure-protobuf` contributors © 2011-2019
"""
from io import BytesIO
from typing import Any, List, Optional

from pytest import mark, raises

from pure_protobuf.enums import WireType
from pure_protobuf.fields import NonRepeatedField, PackedRepeatedField, UnpackedRepeatedField
from pure_protobuf.serializers import (
    BytesSerializer,
    Serializer,
    StringSerializer,
    UnsignedVarintSerializer,
    unsigned_varint_serializer,
)


@mark.parametrize(
    "value, bytes_",
    [
        (b"testing", b"\x0A\x07testing"),
    ],
)
def test_non_repeated_field(value: bytes, bytes_: bytes):
    field = NonRepeatedField(1, "a", BytesSerializer(), False)
    assert field.dumps(value) == bytes_
    with BytesIO(bytes_) as io:
        assert field.load(WireType(UnsignedVarintSerializer().load(io) & 0b111), io) == value


@mark.parametrize(
    "value, expected",
    [
        (1, b"\x08\x01"),
        (None, b""),
    ],
)
def test_optional_non_repeated_field(value: Optional[int], expected: bytes):
    assert NonRepeatedField(1, "a", UnsignedVarintSerializer(), True).dumps(value) == expected


@mark.parametrize(
    "value",
    [
        None,
    ],
)
def test_non_repeated_field_value_error(value: Optional[int]):
    with raises(ValueError):
        NonRepeatedField(1, "a", UnsignedVarintSerializer(), False).validate(value)


@mark.parametrize(
    "value, bytes_",
    [
        ([], b"\x0A\x00"),
        ([3], b"\x0A\x01\x03"),
        ([4, 5], b"\x0A\x02\x04\x05"),
    ],
)
def test_packed_repeated_field(value: List[int], bytes_: bytes):
    field = PackedRepeatedField(1, "a", UnsignedVarintSerializer())
    assert field.dumps(value) == bytes_
    with BytesIO(bytes_) as io:
        assert field.load(WireType(UnsignedVarintSerializer().load(io) & 0b111), io) == value


@mark.parametrize(
    "serializer, value, bytes_",
    [
        (unsigned_varint_serializer, [], b""),
        (unsigned_varint_serializer, [3], b"\x08\x03"),
        (unsigned_varint_serializer, [4, 5], b"\x08\x04\x08\x05"),
        (StringSerializer(), ["None"], b"\x0A\x04None"),
    ],
)
def test_unpacked_repeated_field_dumps(serializer: Serializer, value: List[Any], bytes_: bytes):
    assert UnpackedRepeatedField(1, "a", serializer).dumps(value) == bytes_


@mark.parametrize(
    "serializer, value, bytes_",
    [
        # Key is omitted because it's being read in the message serializer.
        (unsigned_varint_serializer, [3], b"\x03"),
        (StringSerializer(), ["None"], b"\x04None"),
    ],
)
def test_unpacked_repeated_field_load(serializer: Serializer, value: List[Any], bytes_: bytes):
    assert (
        UnpackedRepeatedField(1, "a", serializer).load(serializer.wire_type, BytesIO(bytes_))
        == value
    )
