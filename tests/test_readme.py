# coding: utf-8

"""
Tests code snippets in ``README.md``.

`pure-protobuf` contributors © 2011-2019
"""

import re
import sys
from os.path import dirname, join

from pytest import mark, skip

code_block_re = re.compile(r'^```python$(.*?)^```$', re.MULTILINE | re.DOTALL)
readme = open(join(dirname(dirname(__file__)), 'README.md'), 'rt').read()


@mark.parametrize('code', code_block_re.findall(readme))
def test_code_block(code):
    if code.lstrip().startswith('# Python 3.6+') and sys.version_info < (3, 6, 0, 0):
        skip('Python 3.6+ is needed')
    exec(code, {})  # skipcq: PYL-W0122
