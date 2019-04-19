"""
Google Protocol Buffers well-known types.

`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32, int64


@dataclass
class TimeSpan:
    """
    Base class to represent timespan as whole seconds plus its nanoseconds part.
    """
    seconds: int64 = field(1, default=0)
    nanos: int32 = field(2, default=0)


@message
@dataclass
class Timestamp(TimeSpan):
    """
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/timestamp.proto
    """


@message
@dataclass
class Duration(TimeSpan):
    """
    See also: https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#duration
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/duration.proto
    """


# noinspection PyPep8Naming
@message
@dataclass
class Any_:
    """
    See also: https://github.com/protocolbuffers/protobuf/blob/master/src/google/protobuf/any.proto
    """
    type_url: str = field(1, default='')
    value: bytes = field(2, default=b'')
