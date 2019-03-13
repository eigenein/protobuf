"""
`pure-protobuf` contributors © 2011-2019
"""

from enum import IntEnum


# Wire types.
# See also https://developers.google.com/protocol-buffers/docs/encoding#structure
class WireType(IntEnum):
    VARINT = 0
    LONG_LONG = 1  # 64 bit
    BYTES = 2
    LONG = 5  # 32 bit
