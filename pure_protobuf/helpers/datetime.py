from math import modf
from typing import Tuple


def split_seconds(seconds: float) -> Tuple[int, int]:
    """Split seconds into whole seconds and nanoseconds."""
    fraction, whole = modf(seconds)
    return int(whole), int(fraction * 1_000_000_000.0)


def unsplit_seconds(seconds: int, nanos: int) -> float:
    """Merge whole seconds and nanoseconds back to normal seconds."""
    return float(seconds) + float(nanos) / 1_000_000_000.0
