"""Tests code snippets in the `README.md`."""

import re
from os.path import dirname, join

from pytest import mark

code_block_re = re.compile(r"^```python$(.*?)^```$", re.MULTILINE | re.DOTALL)
readme = open(join(dirname(dirname(__file__)), "README.md"), "rt").read()


@mark.parametrize("code", code_block_re.findall(readme))
def test_code_block(code):
    exec(code, {})  # skipcq: PYL-W0122
