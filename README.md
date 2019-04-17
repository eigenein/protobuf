# `pure-protobuf`

Python implementation of [Protocol Buffers](http://code.google.com/apis/protocolbuffers/docs/encoding.html) data types.

[![Build Status](https://travis-ci.org/eigenein/protobuf.svg?branch=master)](https://travis-ci.org/eigenein/protobuf)
[![Coverage Status](https://coveralls.io/repos/github/eigenein/protobuf/badge.svg?branch=master)](https://coveralls.io/github/eigenein/protobuf?branch=master)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
[![License](https://img.shields.io/pypi/l/pure-protobuf.svg)](https://github.com/eigenein/protobuf/blob/master/LICENSE)

## Dataclasses

`pure-protobuf` allows you to take advantages of the standard [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module to define message types. It is preferred over the legacy interface for new projects. The dataclasses interface is available in Python 3.6 and higher.

The legacy interface is deprecated and still available via `pure_protobuf.legacy`.

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
# Python 3.6+

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

`typing.List` and `typing.Iterable` annotations are automatically converted to repeated fields. Repeated fields of scalar numeric types use packed encoding by default:

```python
# Python 3.6+

from dataclasses import dataclass
from typing import List

from pure_protobuf.dataclasses_ import field, message
from pure_protobuf.types import int32


@message
@dataclass
class Message:
    foo: List[int32] = field(1, default_factory=list)
```

It's also possible to wrap a field type with [`typing.Optional`](https://docs.python.org/3/library/typing.html#typing.Optional). If `None` is assigned to an `Optional` field, then the field will be skipped during serialization.

### Default values

In `pure-protobuf` it's developer's responsibility to take care of default values. If encoded message does not contain a particular element, the corresponding field stays unassigned. It means that the standard `default` and `default_factory` parameters of the `field` function work as usual.

### Enumerations

Subclasses of the standard [`IntEnum`](https://docs.python.org/3/library/enum.html#intenum) class are supported:

```python
# Python 3.6+

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
# Python 3.6+

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

| Python     | `pure_protobuf.types.google` | `.proto`    |
| ---------- | ---------------------------- | ----------- |
| `datetime` | `Timestamp`                  | `Timestamp` |
| TODO       | `Any_`                       | `Any`       |

Python types are handled automatically, you have nothing to do but use them normally in type hints:

```python
# Python 3.6+

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pure_protobuf.dataclasses_ import field, message


@message
@dataclass
class Test:
    timestamp: Optional[datetime] = field(0, default=None)
```

## Legacy interface

Assume you have the following definition:

```proto
message Test2 {
  string b = 2;
}
```
    
This is how you can create a message and get it serialized:

```python
from io import BytesIO

from pure_protobuf.legacy import MessageType, Unicode

# Create the type instance and add the field.
type_ = MessageType()
type_.add_field(2, 'b', Unicode)

message = type_()
message.b = 'testing'

# Dump into a string.
assert message.dumps() == b'\x12\x07testing'

# Dump into a file-like object.
fp = BytesIO()
message.dump(fp)

# Load from a string.
assert type_.loads(message.dumps()) == message

# Load from a file-like object.
fp.seek(0)
assert type_.load(fp) == message
```

### Required field

To add a missing field you should pass an additional `flags` parameter to `add_field` like this:

```python
from pure_protobuf.legacy import Flags, MessageType, Unicode

type_ = MessageType()
type_.add_field(2, 'b', Unicode, flags=Flags.REQUIRED)

message = type_()
message.b = 'hello, world'

assert type_.dumps(message)
```
    
If you'll not fill in a required field, then `ValueError` will be raised during serialization.

### Repeated field

```python
from pure_protobuf.legacy import Flags, MessageType, UVarint

type_ = MessageType()
type_.add_field(1, 'b', UVarint, flags=Flags.REPEATED)

message = type_()
message.b = (1, 2, 3)

assert type_.dumps(message)
```
    
Value of a repeated field can be any iterable object. The loaded value will always be `list`.

### Packed repeated field

```python
from pure_protobuf.legacy import Flags, MessageType, UVarint

type_ = MessageType()
type_.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)

message = type_()
message.d = (3, 270, 86942)

assert type_.dumps(message)
```
    
### Embedded messages

```proto
message Test1 {
  int32 a = 1;
}

message Test3 {
  required Test1 c = 3;
}
```
    
To create an embedded field, wrap inner type with `EmbeddedMessage`:

```python
from pure_protobuf.legacy import EmbeddedMessage, MessageType, UVarint

inner_type = MessageType()
inner_type.add_field(1, 'a', UVarint)
outer_type = MessageType()
outer_type.add_field(3, 'c', EmbeddedMessage(inner_type))

message = outer_type()
message.c = inner_type()
message.c.a = 150

assert outer_type.dumps(message)
```
    
### Data types

| Type      | Python  | Description                        |
|-----------|---------|------------------------------------|
| `UVarint` | `int`   | unsigned integer (variable length) |
| `Varint`  | `int`   | signed integer (variable length)   |
| `Bool`    | `bool`  | boolean                            |
| `Fixed64` | `bytes` | 8-byte string                      |
| `UInt64`  | `int`   | C 64-bit `unsigned long long`      |
| `Int64`   | `int`   | C 64-bit `long long`               |
| `Float64` | `float` | C `double`                         |
| `Fixed32` | `bytes` | 4-byte string                      |
| `UInt32`  | `int`   | C 32-bit `unsigned int`            |
| `Int32`   | `int`   | C 32-bit `int`                     |
| `Float32` | `float` | C `float`                          |
| `Bytes`   | `bytes` | byte string                        |
| `Unicode` | `str`   | unicode string                     |

### Some techniques

#### Streaming messages

The Protocol Buffers format is not self-delimiting. But you can wrap your message type with `EmbeddedMessage` and write or read messages sequentially.

#### `add_field` chaining

`add_field` return the message type itself, thus you can do so:

```python
from pure_protobuf.legacy import EmbeddedMessage, MessageType, UVarint

MessageType().add_field(1, 'a', EmbeddedMessage(MessageType().add_field(1, 'a', UVarint)))
```
