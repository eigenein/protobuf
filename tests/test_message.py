from dataclasses import dataclass
from typing import ClassVar, Optional

from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf


def test_initialize_dataclass_with_one_of() -> None:
    """Verify the fix for https://github.com/eigenein/protobuf/issues/171."""

    @dataclass
    class Message(BaseMessage):
        payload: ClassVar[OneOf] = OneOf()

        foo: Annotated[Optional[int], Field(1, one_of=payload)] = None
        bar: Annotated[Optional[bool], Field(2, one_of=payload)] = None

    assert Message(foo=3).foo == 3
