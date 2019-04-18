"""
`pure-protobuf` contributors © 2011-2019
"""

# noinspection PyCompatibility
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from pure_protobuf.dataclasses_ import field, message


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
