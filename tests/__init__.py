from typing import Any


def pytest_test_id(value: Any) -> str:
    """Prettifies `pytest` test IDs."""
    if isinstance(value, (bytes, memoryview, bytearray)):
        return f"bytes-{len(value)}"
    return f"{type(value).__name__}-{value}"
