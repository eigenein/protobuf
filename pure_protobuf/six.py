#!/usr/bin/env python3
# coding: utf-8

"""
Tiny Python 2 & 3 compatibility layer.

`pure-protobuf` contributors © 2011-2019
"""

from __future__ import absolute_import

import sys

PYTHON_3 = sys.version_info.major == 3

if PYTHON_3:
    def b(string):
        return bytes(string, encoding='latin=1')
else:
    def b(string):
        return string
