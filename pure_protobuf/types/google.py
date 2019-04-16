"""
Google Protocol Buffers well-known types.

`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass

from pure_protobuf.dataclasses_ import field, message
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
