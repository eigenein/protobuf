# `pure-protobuf`

[![Build Status](https://github.com/eigenein/protobuf/workflows/check/badge.svg)](https://github.com/eigenein/protobuf/actions)
[![Coverage Status](https://coveralls.io/repos/github/eigenein/protobuf/badge.svg?branch=master)](https://coveralls.io/github/eigenein/protobuf?branch=master)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypistats.org/packages/pure-protobuf)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
[![License](https://img.shields.io/pypi/l/pure-protobuf.svg)](https://github.com/eigenein/protobuf/blob/master/LICENSE)

This guide describes how to use `pure-protobuf` to structure your data. It tries to follow [the standard developer guide](https://developers.google.com/protocol-buffers/docs/proto3). It also assumes that you're familiar with Protocol Buffers.

### Defining a message type

Let's look at [the simple example](https://developers.google.com/protocol-buffers/docs/proto3#simple). Here's how it looks like in `proto3` syntax:

```proto
syntax = "proto3";

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 result_per_page = 3;
}
```

And this is how you define it with `pure-protobuf`:

```python
from dataclasses import dataclass

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32


@message
@dataclass
class SearchRequest:
    query: str = field(1, default='')
    page_number: int32 = field(2, default=int32(0))
    result_per_page: int32 = field(3, default=int32(0))
   

assert SearchRequest(
    query='hello',
    page_number=int32(1),
    result_per_page=int32(10),
).dumps() == b'\x0A\x05hello\x10\x01\x18\x0A'
```

Keep in mind that `@message` decorator **must** stay on top of [`@dataclass`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass).

### Serializing

Each class wrapped with `@message` gets two methods attached:
- `dumps() -> bytes` to serialize message into a byte string
- `dump(io: IO)` to serialize message into a file-like object

### Deserializing

Each classes wrapped with `@message` gets two class methods attached:
- `loads(bytes_: bytes) -> TMessage` to deserialize a message from a byte string
- `load(io: IO) -> TMessage` to deserialize a message from a file-like object

These methods are also available as standalone functions in `pure_protobuf.dataclasses_`:
- `load(cls: Type[T], io: IO) -> T`
- `loads(cls: Type[T], bytes_: bytes) -> T`

### Specifying field types

In `pure-protobuf` types are specified with [type hints](https://www.python.org/dev/peps/pep-0484/). Native Python `float`, `str`, `bytes` and `bool` types are supported. Since other Protocol Buffers types don't exist as native Python types, the package uses [`NewType`](https://docs.python.org/3/library/typing.html#newtype) to define them. They're available via `pure_protobuf.types` and named in the same way.

### Assigning field numbers

Field numbers are provided via the `metadata` parameter of the [`field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) function: `field(..., metadata={'number': number})`. However, to improve readability and save some characters, `pure-protobuf` provides a helper function `pure_protobuf.dataclasses_.field` which accepts field number as the first positional parameter and just passes it to the standard `field` function.

### Specifying field rules

[`typing.List`](https://docs.python.org/3/library/typing.html#typing.List) and [`typing.Iterable`](https://docs.python.org/3/library/typing.html#typing.Iterable) annotations are automatically converted to [repeated fields](https://developers.google.com/protocol-buffers/docs/proto3#specifying-field-rules). Repeated fields of scalar numeric types use packed encoding by default:

```python
from dataclasses import dataclass
from typing import List

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32


@message
@dataclass
class Message:
    foo: List[int32] = field(1, default_factory=list)
```

In case, unpacked encoding is explicitly wanted, the `packed`-argument of `field` can be used as in:

```python
from dataclasses import dataclass
from typing import List

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32

@message
@dataclass
class Message:
    foo: List[int32] = field(1, default_factory=list, packed=False)
```

It's also possible to wrap a field type with [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional). If `None` is assigned to an `Optional` field, then the field will be skipped during serialization.

### Default values

In `pure-protobuf` it's developer's responsibility to take care of default values. If encoded message does not contain a particular element, the corresponding field stays unassigned. It means that the standard `default` and `default_factory` parameters of the `field` function work as usual:

```python
from dataclasses import dataclass
from typing import Optional

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32


@message
@dataclass
class Foo:
    bar: int32 = field(1, default=42)
    qux: Optional[int32] = field(2, default=None)


assert Foo().dumps() == b'\x08\x2A'
assert Foo.loads(b'') == Foo(bar=42)
```

In fact, the pattern `qux: Optional[int32] = field(2, default=None)` is so common that there's a convenience function `optional_field` to define an `Optional` field with `None` value by default:

```python
from dataclasses import dataclass
from typing import Optional

from pure_protobuf.dataclasses_ import optional_field, message
from pure_protobuf.types import int32


@message
@dataclass
class Foo:
    qux: Optional[int32] = optional_field(2)


assert Foo().dumps() == b''
assert Foo.loads(b'') == Foo(qux=None)
```

### Enumerations

Subclasses of the standard [`IntEnum`](https://docs.python.org/3/library/enum.html#intenum) class are supported:

```python
from dataclasses import dataclass
from enum import IntEnum

from pure_protobuf.dataclasses_ import field, message


class TestEnum(IntEnum):
    BAR = 1


@message
@dataclass
class Test:
    foo: TestEnum = field(1)


assert Test(foo=TestEnum.BAR).dumps() == b'\x08\x01'
assert Test.loads(b'\x08\x01') == Test(foo=TestEnum.BAR)
```

### Using other message types

Embedded messages are defined the same way as normal dataclasses:

```python
from dataclasses import dataclass

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32


@message
@dataclass
class Test1:
    a: int32 = field(1, default=0)


@message
@dataclass
class Test3:
    c: Test1 = field(3, default_factory=Test1)


assert Test3(c=Test1(a=int32(150))).dumps() == b'\x1A\x03\x08\x96\x01'
```

### Well-known message types

`pure_protobuf.google` also provides built-in definitions for the following [well-known message types](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf):

| Annotation   | `pure_protobuf.types.google` | `.proto`    |
| ------------ | ---------------------------- | ----------- |
| `datetime`   | `Timestamp`                  | `Timestamp` |
| `timedelta`  | `Duration`                   | `Duration`  |
| `typing.Any` | `Any_`                       | `Any`       |

They're handled automatically, you have nothing to do but use them normally in type hints:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pure_protobuf.dataclasses_ import field, message


@message
@dataclass
class Test:
    timestamp: Optional[datetime] = field(1, default=None)
```

#### [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)

Since `pure-protobuf` is not able to download or parse `.proto` definitions, it provides a limited implementation of the [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any) message type. That is, you still have to define all message classes in the usual way. Then, `pure-protobuf` will be able to import and instantiate an encoded value:

```python
from dataclasses import dataclass
from typing import Any, Optional

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types.google import Timestamp


@message
@dataclass
class Message:
    value: Optional[Any] = field(1)


# Here `Timestamp` is used just as an example, in principle any importable user type works.
message = Message(value=Timestamp(seconds=42))
assert Message.loads(message.dumps()) == message
```
