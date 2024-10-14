from dataclasses import dataclass
from typing import Annotated
from urllib.parse import urlunparse

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.well_known import Any_


@dataclass
class ChildMessage(BaseMessage):
    foo: Annotated[int, Field(1)]


def test_child() -> None:
    child = ChildMessage(foo=42)
    any_ = Any_.from_message(child)
    assert urlunparse(any_.type_url) == "import://tests.test_well_known/ChildMessage"
    assert any_.into_message() == child
