from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.well_known import Any_


@dataclass
class ChildMessage(BaseMessage):
    foo: Annotated[int, Field(1)]


def test_child() -> None:
    child = ChildMessage(foo=42)
    any_ = Any_.from_message(child)
    assert any_.type_url.scheme == "import"
    assert any_.type_url.hostname == "tests.test_well_known"
    assert any_.type_url.path == "/ChildMessage"
    assert any_.into_message() == child
