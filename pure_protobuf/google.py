"""
Google Protocol Buffers well-known types.

`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass
from datetime import datetime, timezone
from math import modf
from typing import Any, Dict, Type

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.io_ import IO
from pure_protobuf.serializers import MessageSerializer, PackingSerializer, Serializer
from pure_protobuf.types import int32, int64


@message
@dataclass
class Timestamp:
    """
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto
    """
    seconds: int64 = field(1)
    nanos: int32 = field(2)


# noinspection PyPep8Naming
@message
@dataclass
class Any_:
    """
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/any.proto
    """
    type_url: str = field(1, default='')
    value: bytes = field(2, default=b'')


class DateTimeSerializer(MessageSerializer):
    """
    Supports ``datetime`` as ``Timestamp`` well-known type.
    """

    def __init__(self):
        super().__init__(Timestamp)

    def validate(self, value: Any):
        if not isinstance(value, datetime):
            raise ValueError(f'`datetime` expected, got `{type(value)}`')

    def dump(self, value: Any, io: IO):
        fraction, whole = modf(value.timestamp())
        super().dump(Timestamp(seconds=int64(int(whole)), nanos=int32(int(fraction * 1_000_000_000.0))), io)

    def load(self, io: IO) -> Any:
        timestamp: Timestamp = super().load(io)
        return datetime.fromtimestamp(
            float(timestamp.seconds) + float(timestamp.nanos) / 1_000_000_000.0,
            tz=timezone.utc,
        )


SERIALIZERS: Dict[Type, Serializer] = {
    # TODO: Any
    datetime: PackingSerializer(DateTimeSerializer()),
}
