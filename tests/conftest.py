from io import BytesIO
from typing import Callable, Dict, Tuple

from pytest import fixture


@fixture
def bytes_io() -> Callable[[bytes], Callable[[], Tuple[Tuple[BytesIO], Dict]]]:
    def make_setup(bytes_: bytes) -> Callable[[], Tuple[Tuple[BytesIO], Dict]]:
        """Make `setup` function for `pytest-benchmark`."""

        def setup() -> Tuple[Tuple[BytesIO], Dict]:
            return (BytesIO(bytes_),), {}

        return setup

    return make_setup
