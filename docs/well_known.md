# Well-known types

`#!python pure_protobuf.well_known` module provides message definitions for some of the [well-known](https://protobuf.dev/reference/protobuf/google.protobuf/) types.

## [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)

Since `pure-protobuf` is not able to download or parse `.proto` definitions, it provides a limited implementation of the [`#!protobuf Any`](https://developers.google.com/protocol-buffers/docs/proto3#any) message type. That is, you still have to conventionally define message classes and make them importable (similarly to the [`pickle`](https://docs.python.org/3/library/pickle.html) behaviour):

```python title="test_any.py"
from urllib.parse import urlunparse

from pure_protobuf.well_known import Any_

# The class must be importable:
from tests.test_well_known import ChildMessage
# @dataclass
# class ChildMessage(BaseMessage):
#     foo: Annotated[int, Field(1)]


child = ChildMessage(foo=42)
any_ = Any_.from_message(child)
assert urlunparse(any_.type_url) == "import://tests.test_well_known/ChildMessage"
assert any_.into_message() == child
```

!!! warning "Type URL format"

    Please, consider the URL format a part of the public API. This means, in particular, that future major version bumps may change the format in a backwards-incompatible way.

## `#!python Timestamp`

Implements the [`#!protobuf Timestamp`](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#timestamp) well-known type and supports conversion from and to `datetime` via `from_datetime` and `into_datetime`.

## `#!python Duration`

Implements the [`#!protobuf Duration`](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#duration) well-known type and supports conversion from and to `timedelta` via `from_timedelta` and `into_timedelta`.
