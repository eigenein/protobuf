from dataclasses import dataclass
from urllib.parse import urlunparse

from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.well_known import Any_


@dataclass
class ChildMessage(BaseMessage):
    foo: Annotated[int, Field(1)]


def test_child():
    child = ChildMessage(foo=42)
    any_ = Any_.from_message(child)
    assert urlunparse(any_.type_url) == "import://tests.test_well_known/ChildMessage"
    assert any_.into_message() == child
