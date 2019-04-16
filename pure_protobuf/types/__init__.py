"""
Type hints for the dataclasses interface.
Defines custom Protocol Buffers types that don't exist as native types in Python.
See also: https://developers.google.com/protocol-buffers/docs/proto3#scalar

`pure-protobuf` contributors © 2011-2019
"""

from typing import NewType

double = NewType('double', float)
fixed32 = NewType('fixed32', int)
fixed64 = NewType('fixed64', int)
sfixed32 = NewType('sfixed32', int)
sfixed64 = NewType('sfixed64', int)
sint32 = NewType('sint32', int)
sint64 = NewType('sint64', int)
uint = NewType('uint', int)  # is not a part of the standard
uint32 = NewType('uint32', int)
uint64 = NewType('uint64', int)
int32 = uint32  # TODO: is it actually the same?
int64 = uint64  # TODO: is it actually the same?

# Not available in `typing`.
NoneType = type(None)
