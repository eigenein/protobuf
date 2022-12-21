"""Test class definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from typing_extensions import Annotated, Self

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage


class ExampleEnum(IntEnum):
    FOO = 1
    BAR = 2


@dataclass
class RecursiveMessage(BaseMessage):
    payload: Annotated[uint, Field(1)]
    inner: Annotated[Optional[Self], Field(2)] = None
