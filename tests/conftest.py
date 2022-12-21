from io import BytesIO

from pytest import fixture


@fixture
def bytes_io():
    def make_setup(bytes_: bytes):
        """Makes `setup` function for `pytest-benchmark`."""

        def setup():
            return (BytesIO(bytes_),), {}

        return setup

    return make_setup
