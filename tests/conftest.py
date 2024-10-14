from io import BytesIO
from typing import Callable

from pytest import fixture


@fixture
def bytes_io() -> Callable[[bytes], Callable[[], tuple[tuple[BytesIO], dict]]]:
    def make_setup(bytes_: bytes) -> Callable[[], tuple[tuple[BytesIO], dict]]:
        """Make `setup` function for `pytest-benchmark`."""

        def setup() -> tuple[tuple[BytesIO], dict]:
            return (BytesIO(bytes_),), {}

        return setup

    return make_setup
