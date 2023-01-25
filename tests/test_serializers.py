"""
`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, List, Optional, Type

from pytest import fixture, mark, raises

from pure_protobuf.dataclasses_ import OneOf_, field, message, one_of, part
from pure_protobuf.enums import WireType
from pure_protobuf.serializers import (
    BooleanSerializer,
    BytesSerializer,
    DoubleSerializer,
    FloatSerializer,
    IntEnumSerializer,
    PackingSerializer,
    Serializer,
    SignedFixed32Serializer,
    SignedFixed64Serializer,
    SignedInt32Serializer,
    SignedInt64Serializer,
    SignedVarintSerializer,
    StringSerializer,
    TwosComplimentInt32Serializer,
    TwosComplimentInt64Serializer,
    UnsignedFixed32Serializer,
    UnsignedFixed64Serializer,
    UnsignedInt32Serializer,
    UnsignedInt64Serializer,
    UnsignedVarintSerializer,
)
from pure_protobuf.types import int32, uint
from tests import _test_id


@fixture
def class_1() -> Type:
    @message
    @dataclass
    class Test1:
        a: int32 = field(1, default=0)

    return Test1


@fixture
def class_2() -> Type:
    @message
    @dataclass
    class Test2:
        b: Optional[str] = field(2, default=None)

    return Test2


@fixture
def class_3(class_1: Type) -> Type:
    @message
    @dataclass
    class Test3:
        c: class_1 = field(3, default_factory=class_1)  # type: ignore

    return Test3


@mark.parametrize(
    "serializer_class, value",
    [
        (SignedVarintSerializer, "hello"),
        (BytesSerializer, 42),
        (StringSerializer, 42),
        (UnsignedInt32Serializer, 0x1_00000000),
        (UnsignedInt64Serializer, -1),
        (SignedInt32Serializer, 0x80000000),
        (SignedInt64Serializer, 0x80000000_00000000),
        (BooleanSerializer, 42),
        (SignedFixed32Serializer, "hello"),
        (UnsignedFixed32Serializer, "hello"),
        (SignedFixed64Serializer, "hello"),
        (UnsignedFixed64Serializer, "hello"),
        (FloatSerializer, "hello"),
        (DoubleSerializer, "hello"),
        (TwosComplimentInt32Serializer, 1 << 31),
        (TwosComplimentInt64Serializer, 1 << 63),
        (TwosComplimentInt32Serializer, -(1 << 31) - 1),
        (TwosComplimentInt64Serializer, -(1 << 63) - 1),
    ],
)
def test_serializer_value_error(serializer_class: Type[Serializer], value: Any):
    with raises(ValueError):
        serializer_class().validate(value)


UNSIGNED_VARINT_TESTS = [
    (0, b"\x00"),
    (3, b"\x03"),
    (270, b"\x8E\x02"),
    (86942, b"\x9E\xA7\x05"),
]


@mark.parametrize("value, bytes_", UNSIGNED_VARINT_TESTS, ids=_test_id)
def test_unsigned_varint_serializer_dumps(value: int, bytes_: bytes, benchmark):
    UnsignedVarintSerializer().validate(value)
    assert benchmark(UnsignedVarintSerializer().dumps, value) == bytes_


@mark.parametrize("value, bytes_", UNSIGNED_VARINT_TESTS, ids=_test_id)
def test_unsigned_varint_serializer_loads(value: int, bytes_: bytes, benchmark):
    UnsignedVarintSerializer().validate(value)
    assert benchmark(UnsignedVarintSerializer().loads, bytes_) == value


SIGNED_VARINT_TESTS = [
    (0, b"\x00"),
    (-1, b"\x01"),
    (1, b"\x02"),
    (-2, b"\x03"),
]


@mark.parametrize("value, bytes_", SIGNED_VARINT_TESTS, ids=_test_id)
def test_signed_varint_serializer_dumps(value: int, bytes_: bytes, benchmark):
    SignedVarintSerializer().validate(value)
    assert benchmark(SignedVarintSerializer().dumps, value) == bytes_


@mark.parametrize("value, bytes_", SIGNED_VARINT_TESTS, ids=_test_id)
def test_signed_varint_serializer_loads(value: int, bytes_: bytes, benchmark):
    SignedVarintSerializer().validate(value)
    assert benchmark(SignedVarintSerializer().loads, bytes_) == value


TWOS_COMPLEMENT_64_TESTS = [
    (-2, b"\xFE\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x01"),
    (1, b"\x01"),
]


@mark.parametrize("value, bytes_", TWOS_COMPLEMENT_64_TESTS, ids=_test_id)
def test_twos_compliment_64_serializer_dumps(value: int, bytes_: bytes, benchmark):
    TwosComplimentInt64Serializer().validate(value)
    assert benchmark(TwosComplimentInt64Serializer().dumps, value) == bytes_


@mark.parametrize("value, bytes_", TWOS_COMPLEMENT_64_TESTS, ids=_test_id)
def test_twos_compliment_64_serializer_loads(value: int, bytes_: bytes, benchmark):
    TwosComplimentInt64Serializer().validate(value)
    assert benchmark(TwosComplimentInt64Serializer().loads, bytes_) == value


TWOS_COMPLEMENT_32_TESTS = [
    (-2, b"\xFE\xFF\xFF\xFF\x0F"),
    (1, b"\x01"),
    (-30, b"\xE2\xFF\xFF\xFF\x0F")
]


@mark.parametrize("value, bytes_", TWOS_COMPLEMENT_32_TESTS, ids=_test_id)
def test_twos_compliment_32_serializer_dumps(value: int, bytes_: bytes, benchmark):
    TwosComplimentInt32Serializer().validate(value)
    assert benchmark(TwosComplimentInt32Serializer().dumps, value) == bytes_


@mark.parametrize("value, bytes_", TWOS_COMPLEMENT_32_TESTS, ids=_test_id)
def test_twos_compliment_32_serializer_loads(value: int, bytes_: bytes, benchmark):
    TwosComplimentInt32Serializer().validate(value)
    assert benchmark(TwosComplimentInt32Serializer().loads, bytes_) == value


@mark.parametrize(
    "value, bytes_",
    [
        (b"testing", b"\x07testing"),
        (bytearray(b"testing"), b"\x07testing"),
        (memoryview(b"testing"), b"\x07testing"),
    ],
)
def test_bytes_serializer(value: bytes, bytes_: bytes):
    BytesSerializer().validate(value)
    assert BytesSerializer().dumps(value) == bytes_
    assert BytesSerializer().loads(bytes_) == value


@mark.parametrize(
    "value, bytes_",
    [
        ("Привет", b"\x0c\xd0\x9f\xd1\x80\xd0\xb8\xd0\xb2\xd0\xb5\xd1\x82"),
    ],
)
def test_string_serializer(value: str, bytes_: bytes):
    StringSerializer().validate(value)
    assert StringSerializer().dumps(value) == bytes_
    assert StringSerializer().loads(bytes_) == value


@mark.parametrize(
    "value, bytes_",
    [
        (True, b"\x01"),
        (False, b"\x00"),
    ],
)
def test_boolean_serializer(value: bool, bytes_: bytes):
    BooleanSerializer().validate(value)
    assert BooleanSerializer().dumps(value) == bytes_
    assert BooleanSerializer().loads(bytes_) == value


@mark.parametrize(
    "value, bytes_",
    [
        (WireType.VARINT, b"\x00"),
        (WireType.LONG_LONG, b"\x01"),
        (WireType.BYTES, b"\x02"),
        (WireType.LONG, b"\x05"),
    ],
)
def test_int_enum_serializer(value: IntEnum, bytes_: bytes):
    IntEnumSerializer(WireType).validate(value)
    assert IntEnumSerializer(WireType).dumps(value) == bytes_
    assert IntEnumSerializer(WireType).loads(bytes_) == value


@mark.parametrize(
    "value, bytes_",
    [
        (2, b"\x01\x02"),
        (270, b"\x02\x8E\x02"),
    ],
)
def test_packing_serializer(value: int, bytes_: bytes):
    PackingSerializer(UnsignedVarintSerializer()).validate(value)
    assert PackingSerializer(UnsignedVarintSerializer()).dumps(value) == bytes_
    assert PackingSerializer(UnsignedVarintSerializer()).loads(bytes_) == value


def test_class_1(class_1: Any):
    """
    See also: https://developers.google.com/protocol-buffers/docs/encoding#simple
    """
    value = class_1(a=int32(150))
    bytes_ = b"\x08\x96\x01"

    assert class_1.loads(b"") == class_1()
    assert value.dumps() == bytes_
    assert class_1.loads(bytes_) == value


def test_class_1_unknown_field(class_1: Any):
    # fmt: off
    assert class_1.loads(
        b"\x21\x01\x02\x03\x04\x05\x06\x07\x08"  # extra 64-bit
        b"\x35\x01\x02\x03\x04"  # extra 32-bit
        b"\x42\x01\x00"  # extra bytes
        b"\x10\xFF\x01"  # extra varint
        b"\x08\x96\x01"  # field `a`
    ) == class_1(a=int32(150))
    # fmt: on


def test_class_2(class_2: Any):
    """
    See also: https://developers.google.com/protocol-buffers/docs/encoding#strings
    """
    value = class_2(b="testing")
    bytes_ = b"\x12\x07\x74\x65\x73\x74\x69\x6e\x67"

    assert class_2.loads(b"") == class_2()
    assert value.dumps() == bytes_
    assert class_2.loads(bytes_) == value


def test_class_3(class_1: Any, class_2: Any, class_3: Any):
    """
    See also: https://developers.google.com/protocol-buffers/docs/encoding#embedded
    """
    value = class_3(c=class_1(a=int32(150)))
    bytes_ = b"\x1A\x03\x08\x96\x01"

    assert class_3.loads(b"") == class_3()
    assert value.dumps() == bytes_
    assert class_3.loads(bytes_) == value
    with raises(ValueError):
        class_3(c=class_2()).dumps()


def test_merge_repeated_embedded_message():
    # For embedded message fields, the parser merges multiple instances of the same field,
    # as if with the `Message::MergeFrom` method.
    # See also: https://developers.google.com/protocol-buffers/docs/encoding#optional

    @message
    @dataclass
    class Inner:
        foo: List[uint] = field(1, default_factory=list)

    @message
    @dataclass
    class Outer:
        inner: Inner = field(1, default_factory=Inner)

    assert (
        # fmt: off
        Outer.loads(

            b'\x0A\x02\x08\x00'  # foo == [0]
            b'\x0A\x03\x08\x96\x01'  # foo == [150]
        )
        == Outer(inner=Inner(foo=[uint(0), uint(150)]))
        # fmt: on
    )


def test_unpacked_as_packed():
    @message
    @dataclass
    class Test:
        foo: List[uint] = field(1)

    # Protocol buffer parsers must be able to parse repeated fields that were compiled as packed as
    # if they were not packed, and vice versa.
    # See also: https://developers.google.com/protocol-buffers/docs/encoding#packed
    assert Test.loads(b"\x08\x01\x08\x02") == Test(foo=[uint(1), uint(2)])


def test_enum():
    class TestEnum(IntEnum):
        BAR = 1

    @message
    @dataclass
    class Test:
        foo: TestEnum = field(1)

    value = Test(foo=TestEnum.BAR)
    bytes_ = b"\x08\x01"

    assert value.dumps() == bytes_
    assert Test.loads(bytes_) == value


def test_one_of_field():
    # message SubMessage {
    #     string id = 1;
    #     int32 b = 3;
    # }
    #
    # message SampleMessage {
    #   oneof test_oneof {
    #     string name = 4;
    #     SubMessage sub_message = 9;
    #   }
    # }

    @message
    @dataclass
    class SubMessage:
        id: str = field(1)
        b: int32 = field(3)

    @message
    @dataclass
    class SampleMessage:
        test_oneof: OneOf_ = one_of(name=part(str, 4), sub_message=part(SubMessage, 9))

    value = SampleMessage()
    value.test_oneof.sub_message = SubMessage(id="123", b=5)

    # assert with original message from proto lib
    # here could be
    bytes_ = b"J\x07\n\x03123\x18\x05"
    assert value.dumps() == bytes_
    assert SampleMessage.loads(bytes_) == value
    assert SampleMessage.loads(value.dumps()) == value

    # change field and check the same
    value.test_oneof.name = "Some string"
    bytes_ = b'"\x0bSome string'
    assert value.dumps() == bytes_
    assert SampleMessage.loads(bytes_) == value
    assert SampleMessage.loads(value.dumps()) == value


def test_many_messages_with_one_of_field():
    # message A {
    #   oneof msg {
    #     int32 a = 1;
    #     strin b = 2;
    #   }
    # }

    @message
    @dataclass
    class A:
        msg: OneOf_ = one_of(a=part(int32, 1), b=part(str, 2))

    value = A()
    value.msg.a = 42
    bytes_ = b"\x08*"

    value2 = A()
    value2.msg.b = "42"
    bytes_2 = b"\x12\x0242"

    assert value.dumps() == bytes_
    assert A.loads(bytes_) == value
    assert A.loads(value.dumps()) == value

    assert value2.dumps() == bytes_2
    assert A.loads(bytes_2) == value2
    assert A.loads(value2.dumps()) == value2

    assert value.msg.a == 42
