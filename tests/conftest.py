#!/usr/bin/env python3
# coding: utf-8

import sys

collect_ignore = []
if sys.version_info < (3, 6, 0, 0):
    collect_ignore.extend([
        'test_dataclasses.py',
        'test_fields.py',
        'test_google.py',
        'test_serializers.py',
    ])
