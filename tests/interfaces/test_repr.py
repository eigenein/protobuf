from typing import Any

from pytest import mark

from pure_protobuf._accumulators import AccumulateMessages
from pure_protobuf._mergers import MergeMessages
from pure_protobuf.descriptors.record import BOOL_DESCRIPTOR
from pure_protobuf.helpers.itertools import ReadCallback
from pure_protobuf.io.varint import (
    ReadEnum,
    WriteEnum,
    read_unsigned_varint,
    write_zigzag_varint,
)
from pure_protobuf.io.wrappers import ReadRepeated, WriteOptional
from pure_protobuf.message import BaseMessage
from tests.definitions import ExampleEnum


@mark.parametrize(
    ("object_", "expected"),
    [
        (ReadEnum(ExampleEnum), "ReadEnum(ExampleEnum)"),
        (WriteEnum[ExampleEnum](), "WriteEnum[<enum 'ExampleEnum'>]()"),
        (
            WriteOptional[int](write_zigzag_varint),
            "WriteOptional[<class 'int'>](WriteZigZagVarint())",
        ),
        (
            MergeMessages(AccumulateMessages(BaseMessage)),
            "MergeMessages(AccumulateMessages(<class 'pure_protobuf.message.BaseMessage'>))",
        ),
        (
            ReadRepeated(ReadCallback(read_unsigned_varint)),
            "ReadRepeated(ReadCallback(ReadUnsignedVarint()))",
        ),
        (
            BOOL_DESCRIPTOR.read,
            "ReadMaybePacked[<class 'bool'>](ReadCallback(ReadBool()))",
        ),
        (
            BOOL_DESCRIPTOR.write,
            "WriteBool()",
        ),
    ],
)
def test_repr(object_: Any, expected: str) -> None:
    assert repr(object_) == expected
