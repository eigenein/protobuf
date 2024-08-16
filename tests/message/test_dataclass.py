from dataclasses import dataclass, field
from typing import List, Optional

from typing_extensions import Annotated

from pure_protobuf.annotations import Field, ZigZagInt, uint
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf


def test_simple_message() -> None:
    """
    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#simple.
    """

    @dataclass
    class Message(BaseMessage):
        a: Annotated[int, Field(1)] = 0
        b: Annotated[uint, Field(2)] = uint(0)

    message = Message(a=150, b=uint(42))
    bytes_ = b"\x08\x96\x01\x10\x2a"

    assert Message.loads(b"") == Message()
    assert bytes(message) == bytes_
    assert Message.loads(bytes_) == message


def test_simple_message_unknown_field() -> None:
    @dataclass
    class Message(BaseMessage):
        a: Annotated[int, Field(1)] = 0

    # fmt: off
    assert Message.loads(
        b"\x21\x01\x02\x03\x04\x05\x06\x07\x08"  # extra 64-bit
        b"\x35\x01\x02\x03\x04"  # extra 32-bit
        b"\x42\x01\x00"  # extra bytes
        b"\x10\xFF\x01"  # extra varint
        b"\x08\x96\x01",  # field `a`
    ) == Message(a=150)
    # fmt: on


def test_message_with_bytestring() -> None:
    """
    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#strings.
    """

    @dataclass
    class Message(BaseMessage):
        b: Annotated[Optional[str], Field(2)] = None

    message = Message(b="testing")
    bytes_ = b"\x12\x07\x74\x65\x73\x74\x69\x6e\x67"

    assert Message.loads(b"") == Message()
    assert bytes(message) == bytes_
    assert Message.loads(bytes_) == message


def test_embedded_message() -> None:
    """
    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#embedded.
    """

    @dataclass
    class Child(BaseMessage):
        a: Annotated[int, Field(1)] = 0

    @dataclass
    class Parent(BaseMessage):
        c: Annotated[Child, Field(3)] = field(default_factory=Child)

    message = Parent(c=Child(a=150))
    bytes_ = b"\x1a\x03\x08\x96\x01"

    assert Parent.loads(b"") == Parent()
    assert bytes(message) == bytes_
    assert Parent.loads(bytes_) == message


def test_merge_embedded_messages_repeated() -> None:
    """
    For embedded message fields, the parser merges multiple instances of the same field,
    as if with the `Message::MergeFrom` method.

    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#last-one-wins
    """

    @dataclass
    class Inner(BaseMessage):
        foo: Annotated[Optional[List[int]], Field(1, packed=False)] = field(default=None)

    @dataclass
    class Outer(BaseMessage):
        inner: Annotated[Inner, Field(1)] = field(default_factory=Inner)

    assert (
        # fmt: off
        Outer.loads(
            b"\x0a\x00"  # foo == None
            b"\x0a\x02\x08\x00"  # foo == [0]
            b"\x0a\x03\x08\x96\x01"  # foo == [150]
            b"\x0a\x00",  # foo == None
        )
        == Outer(inner=Inner(foo=[0, 150]))
        # fmt: on
    )


def test_merge_embedded_messages_primitive() -> None:
    """Message merger with primitive field."""

    @dataclass
    class Inner(BaseMessage):
        foo: Annotated[int, Field(1, packed=False)] = 0

    @dataclass
    class Outer(BaseMessage):
        inner: Annotated[Inner, Field(1)] = field(default_factory=Inner)

    assert (
        # fmt: off
        Outer.loads(
            b"\x0a\x02\x08\x01"  # foo == 1
            b"\x0a\x02\x08\x02",  # foo == 2
        )
        == Outer(inner=Inner(foo=2))
        # fmt: on
    )


def test_read_unpacked_repeated_as_packed() -> None:
    """
    Protocol buffer parsers must be able to parse repeated fields that were compiled as packed as
    if they were not packed, and vice versa.

    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#packed
    """

    @dataclass
    class Test(BaseMessage):
        foo: Annotated[List[int], Field(1, packed=True)]

    assert Test.loads(b"\x08\x01\x08\x02") == Test(foo=[1, 2])


def test_read_packed_repeated_as_unpacked() -> None:
    """
    Protocol buffer parsers must be able to parse repeated fields that were compiled as packed as
    if they were not packed, and vice versa.

    See Also:
    - https://developers.google.com/protocol-buffers/docs/encoding#packed.
    """

    @dataclass
    class Test(BaseMessage):
        foo: Annotated[List[int], Field(1, packed=False)]

    assert Test.loads(b"\x0a\x04\x01\x96\x01\x02") == Test(
        foo=[1, 150, 2],
    )


def test_repeated_embedded_message() -> None:
    @dataclass
    class Child(BaseMessage):
        payload: Annotated[int, Field(2)]

    @dataclass
    class Parent(BaseMessage):
        children: Annotated[List[Child], Field(1)]

    message = Parent(children=[Child(payload=42), Child(payload=43)])
    encoded = bytes(message)
    assert encoded == bytes.fromhex("0a02102a 0a02102b")
    assert Parent.loads(encoded) == message


def test_merge_grandchild() -> None:
    @dataclass
    class Grandchild(BaseMessage):
        payload: Annotated[int, Field(1)]

    @dataclass
    class Child(BaseMessage):
        child: Annotated[Optional[Grandchild], Field(2)] = None

    @dataclass
    class Parent(BaseMessage):
        child: Annotated[Child, Field(1)]

    assert Parent.loads(
        bytes(Parent(child=Child(child=Grandchild(payload=42))))
        + bytes(Parent(child=Child(child=Grandchild(payload=43)))),
    ) == Parent(child=Child(child=Grandchild(payload=43)))

    assert Parent.loads(
        bytes(Parent(child=Child(child=Grandchild(payload=42)))) + bytes(Parent(child=Child())),
    ) == Parent(child=Child(child=Grandchild(payload=42)))


def test_concatenated_packed_repeated() -> None:
    """
    Note that although there's usually no reason to encode more than one key-value pair for a packed repeated field,
    parsers must be prepared to accept multiple key-value pairs.
    In this case, the payloads should be concatenated.

    See Also:
        - https://developers.google.com/protocol-buffers/docs/encoding#packed
    """

    @dataclass
    class Message(BaseMessage):
        field: Annotated[List[int], Field(1, packed=True)]

    part_1 = bytes(Message(field=[42, 43]))
    part_2 = bytes(Message(field=[100500, 100501]))
    assert Message.loads(part_1 + part_2) == Message(field=[42, 43, 100500, 100501])


def test_one_of_assignment_dataclass() -> None:
    @dataclass
    class Message(BaseMessage):
        foo_or_bar = OneOf[Optional[int]]()
        which_foo_or_bar = foo_or_bar.which_one_of_getter()

        foo: Annotated[Optional[int], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[int], Field(2, one_of=foo_or_bar)] = None

    message = Message()
    message.foo = 42
    message.bar = 43

    assert message.foo_or_bar == 43
    assert message.foo is None
    assert message.bar == 43
    assert message.which_foo_or_bar() == "bar"


def test_one_of_read_from() -> None:
    @dataclass
    class Message(BaseMessage):
        foo_or_bar = OneOf[Optional[ZigZagInt]]()
        which_foo_or_bar = foo_or_bar.which_one_of_getter()

        foo: Annotated[Optional[ZigZagInt], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[ZigZagInt], Field(2, one_of=foo_or_bar)] = None

    message = Message.loads(b"\x08\x02\x10\x04")
    assert message.foo_or_bar == 2
    assert message.bar == 2
    assert message.foo is None
    assert message.which_foo_or_bar() == "bar"


def test_one_of_merged() -> None:
    @dataclass
    class Child(BaseMessage):
        foo_or_bar = OneOf[Optional[ZigZagInt]]()
        which_foo_or_bar = foo_or_bar.which_one_of_getter()

        foo: Annotated[Optional[ZigZagInt], Field(1, one_of=foo_or_bar)] = None
        bar: Annotated[Optional[ZigZagInt], Field(2, one_of=foo_or_bar)] = None

    @dataclass
    class Parent(BaseMessage):
        child: Annotated[Child, Field(1)]

    message = Parent.loads(bytes.fromhex("0a020802 0a021004"))
    assert message.child.foo_or_bar == 2
    assert message.child.bar == 2
    assert message.child.foo is None
    assert message.child.which_foo_or_bar() == "bar"
