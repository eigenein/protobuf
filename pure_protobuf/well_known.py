"""Well-known types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Any, Mapping, Optional, Type, cast
from urllib.parse import ParseResult

from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.helpers._dataclasses import DATACLASS_OPTIONS
from pure_protobuf.helpers.datetime import split_seconds, unsplit_seconds
from pure_protobuf.message import BaseMessage


@dataclass(**DATACLASS_OPTIONS)
class _TimeSpan(BaseMessage):
    """Base class to represent timespan as whole seconds plus its nanoseconds part."""

    seconds: Annotated[int, Field(1)] = 0
    nanos: Annotated[int, Field(2)] = 0


@dataclass(**DATACLASS_OPTIONS)
class Timestamp(_TimeSpan):
    """
    Timestamp as a time span since the epoch time.

    See Also:
        - https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#timestamp
        - https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto
    """

    @classmethod
    def from_datetime(cls, value: datetime) -> Timestamp:
        seconds, nanos = split_seconds(value.timestamp())
        return cls(seconds=seconds, nanos=nanos)

    def into_datetime(self) -> datetime:
        return datetime.fromtimestamp(unsplit_seconds(self.seconds, self.nanos), tz=timezone.utc)


@dataclass(**DATACLASS_OPTIONS)
class Duration(_TimeSpan):
    """
    Duration as a time span.

    See Also:
        - https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#duration
        - https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/duration.proto
    """

    @classmethod
    def from_timedelta(cls, value: timedelta) -> Duration:
        seconds, nanos = split_seconds(value.total_seconds())
        return cls(seconds=seconds, nanos=nanos)

    def into_timedelta(self) -> timedelta:
        return timedelta(seconds=unsplit_seconds(self.seconds, self.nanos))


@dataclass(**DATACLASS_OPTIONS)
class Any_:  # noqa: N801
    """
    Well-known `Any` type.

    See Also:
        - https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/any.proto.
    """

    type_url: Annotated[ParseResult, Field(1)]
    value: Annotated[bytes, Field(2)] = b""

    @classmethod
    def from_message(cls, message: BaseMessage) -> Any_:
        """Convert the message into its `Any_` representation."""

        # noinspection PyArgumentList
        return cls(
            type_url=ParseResult(
                scheme="import",
                netloc=message.__module__,
                path=type(message).__qualname__,
                params="",
                query="",
                fragment="",
            ),
            value=bytes(message),
        )

    def into_message(
        self,
        locals_: Optional[Mapping[str, Any]] = None,
        globals_: Optional[Mapping[str, Any]] = None,
    ) -> BaseMessage:
        """
        Reconstructs a message from the current `Any_` representation.

        Args:
            locals_: forwarded to the `__import__` call
            globals_: forwarded to the `__import__` call

        See Also:
            - https://developers.google.com/protocol-buffers/docs/proto3#any
        """

        module = __import__(
            self.type_url.netloc,
            fromlist=[self.type_url.path],
            locals=locals_,
            globals=globals_,
        )
        class_ = cast(Type[BaseMessage], getattr(module, self.type_url.path))
        return class_.read_from(BytesIO(self.value))
