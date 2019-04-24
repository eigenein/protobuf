#!/usr/bin/env python3
# coding: utf-8

"""
Python implementation of Protocol Buffers data types.

`pure-protobuf` contributors © 2011-2019
"""

import sys

if sys.version_info >= (3, 6, 0, 0):
    from pure_protobuf.serializers import read_varint, write_varint  # noqa: F401
