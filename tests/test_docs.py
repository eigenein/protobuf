"""Tests code snippets in the `README.md` and `docs`."""

import re
from itertools import chain
from pathlib import Path
from typing import Iterator, NamedTuple

from pytest import mark, param

CODE_BLOCK_RE = re.compile(r"^```python\n+# test_id=([\w\-]+)\n+$(.*?)^```$", re.MULTILINE | re.DOTALL)
README = (Path(__file__).parent.parent / "README.md").read_text()


def _discover_files() -> Iterator[Path]:
    project_path = Path(__file__).parent.parent
    yield project_path / "README.md"
    yield from Path("docs").rglob("*.md")


def _generate_params(path: Path) -> Iterator[NamedTuple]:
    for (test_id, snippet) in CODE_BLOCK_RE.findall(path.read_text()):
        yield param(snippet, id=test_id)


@mark.parametrize(
    "snippet",
    chain.from_iterable(_generate_params(path) for path in _discover_files()),
)
def test_documentation_snippet(snippet: str) -> None:
    exec(snippet, {})
