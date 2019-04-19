"""
`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from pytest import mark

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types.google import Any_, Duration, Timestamp


@mark.parametrize('type_, expected', [
    (Any_, 'type.googleapis.com/pure_protobuf.types.google.Any_'),
    (Duration, 'type.googleapis.com/pure_protobuf.types.google.Duration'),
    (Timestamp, 'type.googleapis.com/pure_protobuf.types.google.Timestamp'),
])
def test_type_url(type_: Any, expected: str):
    assert type_.type_url == expected


def test_datetime():
    @message
    @dataclass
    class Test:
        timestamp: Optional[datetime] = field(0, default=None)

    test = Test(timestamp=datetime.now(tz=timezone.utc))
    assert Test.loads(test.dumps()) == test


def test_timedelta():
    @message
    @dataclass
    class Test:
        duration: Optional[timedelta] = field(0, default=None)

    test = Test(duration=timedelta(seconds=42.5))
    assert Test.loads(test.dumps()) == test


def test_any():
    @message
    @dataclass
    class Test:
        value: Any = field(1)

    test = Test(value=Timestamp(seconds=42, nanos=100500))
    assert Test.loads(test.dumps()) == test
