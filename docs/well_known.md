from dataclasses import dataclassfrom pure_protobuf.message import BaseMessage

# Well-known types

`#!python pure_protobuf.well_known` module provides message definitions for some [well-known](https://protobuf.dev/reference/protobuf/google.protobuf/) types.

## [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)

Since `pure-protobuf` is not able to download or parse `.proto` definitions, it provides a limited implementation of the [`#!protobuf Any`](https://developers.google.com/protocol-buffers/docs/proto3#any) message type. That is, you still have to conventionally define message classes and make them importable (similarly to the [`pickle`](https://docs.python.org/3/library/pickle.html) behaviour):

```python title="test_any.py"
from dataclasses import dataclass
from typing import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.well_known import Any_

# The class must be importable:
# @dataclass
# class ChildMessage(BaseMessage):
#     foo: Annotated[int, Field(1)]

from tests.test_well_known import ChildMessage


child = ChildMessage(foo=42)
any_ = Any_.from_message(child)
assert any_.type_url.geturl() == "import://tests.test_well_known/ChildMessage"
assert any_.into_message() == child


@dataclass
class ParentMessage(BaseMessage):
    children: Annotated[list[Any_], Field(1)]


parent = ParentMessage(children=[any_])
assert ParentMessage.loads(parent.dumps()) == parent
```

!!! warning "Type URL format"

    Please, consider the URL format a part of the public API. This means, in particular, that future major version bumps may change the format in a backwards-incompatible way.

## `#!python Timestamp`

::: pure_protobuf.well_known.Timestamp
    options:
      heading_level: 3

## `#!python Duration`

::: pure_protobuf.well_known.Duration
    options:
      heading_level: 3
