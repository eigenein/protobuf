# `pure-protobuf`

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/eigenein/protobuf/check.yml?label=checks)](https://github.com/eigenein/protobuf/actions/workflows/check.yml)
[![Code coverage](https://codecov.io/gh/eigenein/protobuf/branch/master/graph/badge.svg?token=bJarwbLlY7)](https://codecov.io/gh/eigenein/protobuf)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypistats.org/packages/pure-protobuf)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
[![License](https://img.shields.io/pypi/l/pure-protobuf.svg)](https://github.com/eigenein/protobuf/blob/master/LICENSE)

<a href="https://eigenein.github.io/protobuf/">
    <img alt="Documentation" height="25em" src="https://img.shields.io/github/actions/workflow/status/eigenein/protobuf/docs.yml?label=documentation&logo=github">
</a>

<small><strong>Wow! Such annotated! Very buffers!</strong></small>

| ⚠️ Note                                                                                                                                   |
|:------------------------------------------------------------------------------------------------------------------------------------------|
| This `README` describes the upcoming **major version update**. For `2.x` please refer to: https://github.com/eigenein/protobuf/tree/2.2.3 |

## Quickstart

### `.proto` definition

```protobuf
syntax = "proto3";

message SearchRequest {
  string query = 1;
  int32 page_number = 2;
  int32 result_per_page = 3;
}
```

### With [data classes](https://docs.python.org/3/library/dataclasses.html)

```python
# test_id=dataclass

from dataclasses import dataclass
from io import BytesIO

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage
from typing_extensions import Annotated


@dataclass
class SearchRequest(BaseMessage):
    query: Annotated[str, Field(1)] = ""
    page_number: Annotated[uint, Field(2)] = 0
    result_per_page: Annotated[uint, Field(3)] = 0


request = SearchRequest(query="hello", page_number=uint(1), result_per_page=uint(10))
buffer = bytes(request)
assert buffer == b"\x0A\x05hello\x10\x01\x18\x0A"
assert SearchRequest.read_from(BytesIO(buffer))
```

### With [`pydantic`](https://docs.pydantic.dev/)

```python
# test_id=pydantic

from io import BytesIO

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage
from pydantic import BaseModel
from typing_extensions import Annotated


class SearchRequest(BaseMessage, BaseModel):
    query: Annotated[str, Field(1)] = ""
    page_number: Annotated[uint, Field(2)] = 0
    result_per_page: Annotated[uint, Field(3)] = 0


request = SearchRequest(query="hello", page_number=uint(1), result_per_page=uint(10))
buffer = bytes(request)
assert buffer == b"\x0A\x05hello\x10\x01\x18\x0A"
assert SearchRequest.read_from(BytesIO(buffer))
```

## Available methods in `BaseMessage`

### `write_to`

```python
from typing import IO

def write_to(self, io: IO[bytes]) -> None:
    ...
```

Serializes the message into the file-like object.

### `__bytes__`

```python
def __bytes__(self) -> bytes:
    ...
```

Wraps `write_to` to allow serializing a message into a byte string via `bytes(message)`.

### `read_from`

```python
from typing import IO
from typing_extensions import Self

def read_from(cls, io: IO[bytes]) -> Self:
    ...
```

Deserializes a message from the file-like object.

## Limitations

`BaseMessage` requires a subclass to be dataclass-like and accept field values via keyword parameters in its `__init__` method. For most cases, one should use something like the built-in `dataclasses` or a third-party package like `pydantic`.

## Defining fields

Field types are specified via [Annotated](https://docs.python.org/3/library/typing.html#typing.Annotated) [type hints](https://www.python.org/dev/peps/pep-0484/). Each field may include a `pure_protobuf.annotations.Field` annotation, otherwise it gets ignored by `BaseMessage`. For older Python versions one can use `typing_extensions.Annotated`.

The following types are supported:

| Type                                                    | .proto Type                | Notes                                                     |
|---------------------------------------------------------|----------------------------|-----------------------------------------------------------|
| `bool`                                                  | `bool`                     |                                                           |
| `bytes`, `bytearray`, `memoryview`, `typing.ByteString` | `bytes`                    | Always deserialized as `bytes`                            |
| `float`                                                 | `float`                    | 32-bit floating-point number                              |
| `int`                                                   | `sint32`, `sint64`         | **Signed** variable-length integer                        |
| `enum.IntEnum`                                          | `enum`, `uint32`, `uint64` | Supported subclasses of `IntEnum` (see the section below) |
| `pure_protobuf.annotations.double`                      | `double`                   | 64-bit floating-point number                              |
| `pure_protobuf.annotations.fixed32`                     | `fixed32`                  |                                                           |
| `pure_protobuf.annotations.fixed64`                     | `fixed64`                  |                                                           |
| `pure_protobuf.annotations.uint`                        | `uint32`, `uint64`         | **Unsigned** variable-length integer                      |
| `pure_protobuf.annotations.sfixed32`                    | `sfixed32`                 |                                                           |
| `pure_protobuf.annotations.sfixed64`                    | `sfixed64`                 |                                                           |
| `str`                                                   | `string`                   |                                                           |
| `urllib.parse.ParseResult`                              | `string`                   | Parsed URL, represented as a string                       |

### Repeated fields

[`typing.List`](https://docs.python.org/3/library/typing.html#typing.List) annotations are automatically converted to [repeated fields](https://developers.google.com/protocol-buffers/docs/proto3#specifying-field-rules). Repeated fields of scalar numeric types use packed encoding by default:

```python
# test_id=repeated

from dataclasses import dataclass, field
from typing import List
from typing_extensions import Annotated

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage


@dataclass
class Message(BaseMessage):
    foo: Annotated[List[uint], Field(1)] = field(default_factory=list)


assert bytes(Message(foo=[uint(1), uint(2)])) == b"\x0A\x02\x01\x02"
```

In case, unpacked encoding is explicitly wanted, you can specify `packed=False`:

```python
# test_id=repeated-unpacked

from dataclasses import dataclass, field
from typing import List
from typing_extensions import Annotated

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage


@dataclass
class Message(BaseMessage):
    foo: Annotated[List[uint], Field(1, packed=False)] = field(default_factory=list)


assert bytes(Message(foo=[uint(1), uint(2)])) == b"\x08\x01\x08\x02"
```

### Required fields

Required fields are [deprecated](https://developers.google.com/protocol-buffers/docs/style#things_to_avoid) in `proto2` and not supported in `proto3`, thus in `pure-protobuf` fields are always optional. `Optional` annotation is accepted for type hinting, but ignored by `BaseMessage`.

### Default values

In `pure-protobuf` it's developer's responsibility to take care of default values. If encoded message does not contain a particular element, the corresponding field stays unprovided:

```python
# test_id=default-values

from dataclasses import dataclass
from io import BytesIO
from typing import Optional
from typing_extensions import Annotated

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage


@dataclass
class Foo(BaseMessage):
    bar: Annotated[uint, Field(1)] = 42
    qux: Annotated[Optional[uint], Field(2)] = None


assert bytes(Foo()) == b"\x08\x2A"
assert Foo.read_from(BytesIO()) == Foo(bar=uint(42))
```

### Enumerations

Subclasses of the standard [`IntEnum`](https://docs.python.org/3/library/enum.html#intenum) class are supported:

```python
# test_id=enums

from dataclasses import dataclass
from enum import IntEnum
from io import BytesIO
from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


class TestEnum(IntEnum):
    BAR = 1


@dataclass
class Test(BaseMessage):
    foo: Annotated[TestEnum, Field(1)]


assert bytes(Test(foo=TestEnum.BAR)) == b"\x08\x01"
assert Test.read_from(BytesIO(b"\x08\x01")) == Test(foo=TestEnum.BAR)
```

### Embedded messages

```python
# test_id=embedded-messages

from dataclasses import dataclass, field
from typing_extensions import Annotated

from pure_protobuf.annotations import Field, uint
from pure_protobuf.message import BaseMessage


@dataclass
class Test1(BaseMessage):
    a: Annotated[uint, Field(1)] = 0


@dataclass
class Test3(BaseMessage):
    c: Annotated[Test1, Field(3)] = field(default_factory=Test1)


assert bytes(Test3(c=Test1(a=150))) == b"\x1A\x03\x08\x96\x01"
```

## [`Oneof`](https://developers.google.com/protocol-buffers/docs/proto3#oneof)

```python
# test_id=one-of

from typing import ClassVar, Optional

from pydantic import BaseModel
from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf
from typing_extensions import Annotated


class Message(BaseMessage, BaseModel):
    # `ClassVar` is needed because this is a descriptor and not a real attribute.
    foo_or_bar: ClassVar[OneOf] = OneOf()
    which_one = foo_or_bar.which_one_of_getter()

    foo: Annotated[Optional[int], Field(1, one_of=foo_or_bar)] = None
    bar: Annotated[Optional[int], Field(2, one_of=foo_or_bar)] = None


message = Message()
message.foo = 42
message.bar = 43

assert message.foo_or_bar == 43
assert message.foo is None
assert message.bar == 43
assert message.which_one() == "bar"
```

### Limitations

- When assigning a one-of member, `BaseMessage` resets the other fields to `None`, regardless of any defaults defined by, for example, `dataclasses.field`.
- The `OneOf` descriptor simply iterates over its members in order to return a `Oneof` value.
- It's impossible to set a value via a `OneOf` descriptor, one needs to assign the value to a specific field.

## Well-known message types

### [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)

Since `pure-protobuf` is not able to download or parse `.proto` definitions, it provides a limited implementation of the [`Any`](https://developers.google.com/protocol-buffers/docs/proto3#any) message type. That is, you still have to conventionally define message classes and make them importable:

```python
# test_id=well-known-any

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

### `pure_protobuf.well_known.Timestamp`

Implements the [`Timestamp`](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#timestamp) well-known type and supports conversion from and to `datetime` via `from_datetime` and `into_datetime`.

### `pure_protobuf.well_known.Duration`

Implements the [`Duration`](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf#duration) well-known type and supports conversion from and to `timedelta` via `from_timedelta` and `into_timedelta`.
