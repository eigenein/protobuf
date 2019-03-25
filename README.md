# `pure-protobuf`

Python implementation of [Protocol Buffers](http://code.google.com/apis/protocolbuffers/docs/encoding.html) data types.

[![Build Status](https://travis-ci.org/eigenein/protobuf.svg?branch=master)](https://travis-ci.org/eigenein/protobuf)
[![Coverage Status](https://coveralls.io/repos/github/eigenein/protobuf/badge.svg?branch=feature%2Fcoveralls)](https://coveralls.io/github/eigenein/protobuf?branch=feature%2Fcoveralls)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
[![License](https://img.shields.io/pypi/l/pure-protobuf.svg)](https://github.com/eigenein/protobuf/blob/master/LICENSE)

## Dataclasses

`pure-protobuf` allows you to take advantages of the standard [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) module to define message types. It is preferred over the legacy interface for new projects. The dataclasses interface is available in Python 3.6 and higher.

The legacy interface is deprecated and still available via `pure_protobuf.legacy`.

This guide describes how to use `pure-protobuf` to structure your data. It tries to follow [the standard developer guide](https://developers.google.com/protocol-buffers/docs/proto3). It also assumes that you're familiar with Protocol Buffers.

### Defining A Message Type

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

### Specifying Field Types

### Assigning Field Numbers

### Specifying Field Rules

### Scalar Value Types

### Default Values

### Enumerations

### Using Other Message Types

## Legacy Interface

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
print(message.dumps())

# Dump into a file-like object.
fp = BytesIO()
message.dump(fp)

# Load from a string.
assert type_.loads(message.dumps()) == message

# Load from a file-like object.
fp.seek(0)
assert type_.load(fp) == message
```

### Sample 2. Required field

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

### Sample 3. Repeated field

```python
from pure_protobuf.legacy import Flags, MessageType, UVarint

type_ = MessageType()
type_.add_field(1, 'b', UVarint, flags=Flags.REPEATED)

message = type_()
message.b = (1, 2, 3)

assert type_.dumps(message)
```
    
Value of a repeated field can be any iterable object. The loaded value will always be `list`.

### Sample 4. Packed repeated field

```python
from pure_protobuf.legacy import Flags, MessageType, UVarint

type_ = MessageType()
type_.add_field(4, 'd', UVarint, flags=Flags.PACKED_REPEATED)

message = type_()
message.d = (3, 270, 86942)

assert type_.dumps(message)
```
    
### Sample 5. Embedded messages

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
