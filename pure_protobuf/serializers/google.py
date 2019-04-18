"""
Google Protocol Buffers well-known types.

`pure-protobuf` contributors © 2011-2019
"""

from datetime import datetime, timedelta, timezone
from math import modf
from typing import Any, Dict, Tuple, Type

from pure_protobuf.io_ import IO
from pure_protobuf.serializers import MessageSerializer, PackingSerializer, Serializer
from pure_protobuf.types import int32, int64
from pure_protobuf.types.google import Duration, Timestamp


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
    # TODO: Any
    datetime: PackingSerializer(TimestampSerializer()),
    timedelta: PackingSerializer(DurationSerializer()),
}
