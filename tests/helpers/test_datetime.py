from pytest import mark

from pure_protobuf.helpers.datetime import split_seconds, unsplit_seconds


@mark.parametrize(
    "total_seconds, seconds, nanos",
    [
        (42.5, 42, 500_000_000),
    ],
)
def test_split_seconds(total_seconds: float, seconds: int, nanos: int):
    assert split_seconds(total_seconds) == (seconds, nanos)


@mark.parametrize(
    "total_seconds, seconds, nanos",
    [
        (42.5, 42, 500_000_000),
    ],
)
def test_unsplit_seconds(total_seconds: float, seconds: int, nanos: int):
    assert unsplit_seconds(seconds, nanos) == total_seconds
