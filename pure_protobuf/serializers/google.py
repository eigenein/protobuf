"""
Google Protocol Buffers well-known types.

`pure-protobuf` contributors © 2011-2019
"""

from datetime import datetime, timedelta, timezone
from importlib import import_module
from math import modf
from typing import Any, Dict, Tuple, Type

from pure_protobuf.dataclasses_ import Message
from pure_protobuf.io_ import IO
from pure_protobuf.serializers import MessageSerializer, PackingSerializer, Serializer
from pure_protobuf.types import int32, int64
from pure_protobuf.types.google import Any_, Duration, Timestamp


class TimestampSerializer(MessageSerializer):
    """
    Supports `datetime` as `Timestamp` well-known type.
    """

    def __init__(self):
        super().__init__(Timestamp)

    def validate(self, value: Any):
        if not isinstance(value, datetime):
            raise ValueError(f'`datetime` expected, got `{type(value)}`')

    def dump(self, value: Any, io: IO):
        super().dump(Timestamp(*split_seconds(value.timestamp())), io)

    def load(self, io: IO) -> Any:
        timestamp: Timestamp = super().load(io)
        return datetime.fromtimestamp(unsplit_seconds(timestamp.seconds, timestamp.nanos), tz=timezone.utc)


class DurationSerializer(MessageSerializer):
    """
    Supports `timedelta` as `Duration` well-known type.
    """

    def __init__(self):
        super().__init__(Duration)

    def validate(self, value: Any):
        if not isinstance(value, timedelta):
            raise ValueError(f'`timedelta` expected, got `{type(value)}`')

    def dump(self, value: Any, io: IO):
        super().dump(Duration(*split_seconds(value.total_seconds())), io)

    def load(self, io: IO) -> Any:
        duration: Duration = super().load(io)
        return timedelta(seconds=unsplit_seconds(duration.seconds, duration.nanos))


class AnySerializer(MessageSerializer):
    """
    Supports `typing.Any` as `Any` well-known type.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#any
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/any.proto
    """

    def __init__(self):
        super().__init__(Any_)

    def validate(self, value: Any):
        if not isinstance(value, Message):
            raise ValueError(f'message type is expected, got `{type(value)}`')

    def dump(self, value: Any, io: IO):
        super().dump(Any_(type_url=value.type_url, value=value.dumps()), io)

    def load(self, io: IO) -> Any:
        # Load instance of `Any` message type.
        any_ = super().load(io)
        # Get module name and class name from the type URL.
        *_, fqn = any_.type_url.rsplit('/', 1)
        module_name, class_name = fqn.rsplit('.', 1)
        # Get the message type and load underlying message.
        type_ = getattr(import_module(module_name), class_name)
        return type_.loads(any_.value)


def split_seconds(seconds: float) -> Tuple[int64, int32]:
    """
    Split seconds into whole seconds and nanoseconds.
    """
    fraction, whole = modf(seconds)
    return int64(int(whole)), int32(int(fraction * 1_000_000_000.0))


def unsplit_seconds(seconds: int64, nanos: int32) -> float:
    """
    Merge whole seconds and nanoseconds back to normal seconds.
    """
    return float(seconds) + float(nanos) / 1_000_000_000.0


SERIALIZERS: Dict[Type, Serializer] = {
    Any: PackingSerializer(AnySerializer()),
    datetime: PackingSerializer(TimestampSerializer()),
    timedelta: PackingSerializer(DurationSerializer()),
}
