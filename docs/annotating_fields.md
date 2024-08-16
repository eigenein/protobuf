# Annotating fields

Field types are specified via [`#!python Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) [type hints](https://www.python.org/dev/peps/pep-0484/). Each field may include a [`#!python Field`][pure_protobuf.annotations.Field] annotation, otherwise it gets ignored by `#!python BaseMessage`. For older Python versions one can use `#!python typing_extensions.Annotated`.

::: pure_protobuf.annotations.Field
    options:
      show_root_heading: true
      heading_level: 2

## Supported types

### Built-in types

| Type                                                                                                                                                                                                                                                                                                                                        | `.proto` type                                                                  | Notes                                                                                                                                                                                                                                  |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `#!python bool`                                                                                                                                                                                                                                                                                                                             | `#!protobuf bool`                                                              | Encoded normally as `#!python int`                                                                                                                                                                                                     |
| [`#!python bytes`](https://docs.python.org/3/library/stdtypes.html#bytes), [`#!python bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray), [`#!python memoryview`](https://docs.python.org/3/library/stdtypes.html#memoryview), [`#!python ByteString`](https://docs.python.org/3/library/typing.html#typing.ByteString) | `#!protobuf bytes`                                                             | Always deserialized as `#!python bytes`                                                                                                                                                                                                |
| `#!python float`                                                                                                                                                                                                                                                                                                                            | `#!protobuf float`                                                             | **32-bit** floating-point number. Use the [additional](#additional-types) `#!python double` type for 64-bit number                                                                                                                     |
| `#!python int`                                                                                                                                                                                                                                                                                                                              | `#!protobuf int32` `#!protobuf int64` `#!protobuf uint32` `#!protobuf uint64`  | [Variable-length integer](https://en.wikipedia.org/wiki/LEB128). For negative values, [two's compliments](https://en.wikipedia.org/wiki/Two%27s_complement) are used. See also the additional `#!python uint` and `#!python ZigZagInt` |
| [`#!python enum.IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)                                                                                                                                                                                                                                                         | `#!protobuf enum` `#!protobuf int32` `#!protobuf int64`                        | Supports subclasses of `#!python IntEnum` (see [enumerations](#enumerations))                                                                                                                                                          |
| `#!python str`                                                                                                                                                                                                                                                                                                                              | `#!protobuf string`                                                            |                                                                                                                                                                                                                                        |
| [`#!python urllib.parse.ParseResult`](https://docs.python.org/3/library/urllib.parse.html#urllib.parse.ParseResult)                                                                                                                                                                                                                         | `#!protobuf string`                                                            | Parsed URL, represented as a string                                                                                                                                                                                                    |

### Additional types

`#!python pure_protobuf.annotations` module provides additional [`#!python NewType`](https://docs.python.org/3/library/typing.html#newtype)s to support different representations of the singular types:

| `#!python pure_protobuf.annotations` type | `.proto` type                           | Python value type | Notes                                                                                            |
|:------------------------------------------|:----------------------------------------|:------------------|:-------------------------------------------------------------------------------------------------|
| `#!python double`                         | `#!protobuf double`                     | `#!python float`  | **64-bit** floating-point number                                                                 |
| `#!python fixed32`                        | `#!protobuf fixed32`                    | `#!python int`    | 32-bit **unsigned** integer                                                                      |
| `#!python fixed64`                        | `#!protobuf fixed64`                    | `#!python int`    | 64-bit **unsigned** integer                                                                      |
| `#!python sfixed32`                       | `#!protobuf sfixed32`                   | `#!python int`    | 32-bit **signed** integer                                                                        |
| `#!python sfixed64`                       | `#!protobuf sfixed64`                   | `#!python int`    | 64-bit **signed** integer                                                                        |
| `#!python uint`                           | `#!protobuf uint32` `#!protobuf uint64` | `#!python int`    | **Unsigned** variable-length integer                                                             |
| `#!python ZigZagInt`                      | `#!protobuf sint32` `#!protobuf sint64` | `#!python int`    | [ZigZag-encoded](https://en.wikipedia.org/wiki/Variable-length_quantity#Zigzag_encoding) integer |

## Repeated fields

[`typing.List`](https://docs.python.org/3/library/typing.html#typing.List),
[`typing.Iterable`](https://docs.python.org/3/library/typing.html#typing.Iterable),
and [`collections.abc.Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)
annotations are automatically converted to [repeated fields](https://developers.google.com/protocol-buffers/docs/proto3#specifying-field-rules). Repeated fields of scalar numeric types use packed encoding by default:

```python title="test_repeated.py"
from dataclasses import dataclass, field
from typing import List
from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class Message(BaseMessage):
    foo: Annotated[List[int], Field(1)] = field(default_factory=list)


assert bytes(Message(foo=[1, 2])) == b"\x0A\x02\x01\x02"
```

In case, unpacked encoding is explicitly wanted, you can specify `#!python packed=False`:

```python title="test_repeated_unpacked.py"
from dataclasses import dataclass, field
from typing import List
from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class Message(BaseMessage):
    foo: Annotated[List[int], Field(1, packed=False)] = field(
        default_factory=list,
    )


assert bytes(Message(foo=[1, 2])) == b"\x08\x01\x08\x02"
```

## Required fields

Required fields are [deprecated](https://developers.google.com/protocol-buffers/docs/style#things_to_avoid) in `proto2` and not supported in `proto3`, thus in `pure-protobuf` fields are always optional. `#!python Optional` annotation is accepted for type hinting, but has no functional meaning for `#!python BaseMessage`.

## Default values

In `pure-protobuf` it's developer's responsibility to take care of default values. If encoded message does not contain a particular element, the corresponding field stays unprovided:

```python title="test_default_values.py" hl_lines="13"
from dataclasses import dataclass
from io import BytesIO
from typing import Optional
from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class Foo(BaseMessage):
    bar: Annotated[int, Field(1)] = 42
    qux: Annotated[Optional[int], Field(2)] = None


assert bytes(Foo()) == b"\x08\x2A"
assert Foo.read_from(BytesIO()) == Foo(bar=42)
```

!!! warning "Make sure to set defaults for non-required fields"

    `pure-protobuf` makes no assumptions on how a message class' `#!python __init__()` handles missing keyword arguments.
    So, if you expect a field to be optional, you **must** specify a default value explicitly –
    just as you normally do with **pydantic** or **dataclasses**.

    Otherwise, a missing record would cause a missing argument error:

    ```python title="test_missing_default.py" hl_lines="17-18"
    from dataclasses import dataclass
    from io import BytesIO
    from typing import Optional

    from pytest import raises
    from typing_extensions import Annotated

    from pure_protobuf.annotations import Field
    from pure_protobuf.message import BaseMessage


    @dataclass
    class Foo(BaseMessage):
        foo: Annotated[Optional[int], Field(1)]


    with raises(TypeError):
        Foo.read_from(BytesIO())
    ```

## Enumerations

Subclasses of the standard [`#!python IntEnum`](https://docs.python.org/3/library/enum.html#intenum) class are supported, their values are encoded as normal `#!python int`-s:

```python title="test_enum.py" hl_lines="10-11 19-20"
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

## Embedded messages

```python title="test_embedded_message.py" hl_lines="15 18"
from dataclasses import dataclass, field
from typing_extensions import Annotated

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage


@dataclass
class Test1(BaseMessage):
    a: Annotated[int, Field(1)] = 0


@dataclass
class Test3(BaseMessage):
    c: Annotated[Test1, Field(3)] = field(default_factory=Test1)


assert bytes(Test3(c=Test1(a=150))) == b"\x1A\x03\x08\x96\x01"
```

!!! tip "Self-referencing messages"

    Use `#!python typing.Self` (or `#!python typing_extensions.Self` in older Python) to reference
    the message class itself:

    ```python title="test_self.py" hl_lines="13"
    from dataclasses import dataclass    
    from typing import Optional

    from typing_extensions import Annotated, Self

    from pure_protobuf.annotations import Field
    from pure_protobuf.message import BaseMessage


    @dataclass
    class RecursiveMessage(BaseMessage):
        payload: Annotated[int, Field(1)]
        inner: Annotated[Optional[Self], Field(2)] = None
    ```

!!! warning "Messages with circular dependencies are not supported"

    The following example does not work at the moment:

    ```python
    class A(BaseMessage):
        b: Annotated[B, ...]

    class B(BaseMessage):
        a: Annotated[A, ...]
    ```

    Tracking issue: [#108](https://github.com/eigenein/protobuf/issues/108).

## [Oneof](https://developers.google.com/protocol-buffers/docs/proto3#oneof)

```python title="test_one_of.py" hl_lines="11 12 14 15"
from typing import ClassVar, Optional

from pydantic import BaseModel
from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from pure_protobuf.one_of import OneOf
from typing_extensions import Annotated


class Message(BaseMessage, BaseModel):
    foo_or_bar: ClassVar[OneOf] = OneOf()  # (1)
    which_one = foo_or_bar.which_one_of_getter()  # (2)

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

1. `#!python ClassVar` is needed here because this is a descriptor and not a real attribute.
2. Since the `#!python foo_or_bar` returns the value itself, we need an extra attribute for the `#!python which_one()` getter.

!!! warning "Limitations"

    - When assigning a one-of member, `#!python BaseMessage` resets the other fields to `#!python None`, **regardless** of any defaults defined by, for example, `#!python dataclasses.field`.
    - The `#!python OneOf` descriptor simply iterates over its members in order to return an assigned `Oneof` value, so it takes [linear time](https://en.wikipedia.org/wiki/Time_complexity#Linear_time).
    - It's impossible to set a value via a `OneOf` descriptor, one needs to assign the value to a specific attribute.

::: pure_protobuf.one_of.OneOf
    options:
      heading_level: 3
