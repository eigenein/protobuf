from io import BytesIO
from typing import ClassVar, Optional

from pydantic import BaseModel
from typing_extensions import Annotated

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf


def test_simple_message():
    class Message(BaseMessage, BaseModel):
        a: Annotated[uint, Field(1)] = uint(0)

    message = Message(a=uint(150))
    bytes_ = b"\x08\x96\x01"

    assert Message.read_from(BytesIO()) == Message()
    assert bytes(message) == bytes_
    assert Message.read_from(BytesIO(bytes_)) == message


def test_one_of_assignment_pydantic():
    class Message(BaseMessage, BaseModel):
        foo_or_bar: ClassVar[OneOf] = OneOf()

        foo: Annotated[Optional[int], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[int], Field(2, one_of=foo_or_bar)] = None

    message = Message()
    message.foo = 42
    message.bar = 43

    assert message.foo_or_bar == 43
    assert message.foo is None
    assert message.bar == 43


def test_one_of_read_from():
    class Message(BaseMessage, BaseModel):
        foo_or_bar: ClassVar[OneOf] = OneOf()

        foo: Annotated[Optional[int], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[int], Field(2, one_of=foo_or_bar)] = None

    message = Message.read_from(BytesIO(b"\x08\x02\x10\x04"))
    assert message.foo_or_bar == 2
    assert message.bar == 2
    assert message.foo is None


def test_one_of_merged():
    class Child(BaseMessage, BaseModel):
        foo_or_bar: ClassVar[OneOf] = OneOf()

        foo: Annotated[Optional[int], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[int], Field(2, one_of=foo_or_bar)] = None

    class Parent(BaseMessage, BaseModel):
        child: Annotated[Child, Field(1)]

    message = Parent.read_from(BytesIO(bytes.fromhex("0a020802 0a021004")))
    assert message.child.foo_or_bar == 2
    assert message.child.bar == 2
    assert message.child.foo is None
