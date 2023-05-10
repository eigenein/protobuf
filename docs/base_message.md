# Base message

## Available methods

### Serialization into a [file object](https://docs.python.org/3/glossary.html#term-file-object)

```python title="test_write_to.py"
from dataclasses import dataclass

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from typing_extensions import Annotated


@dataclass
class Message(BaseMessage):
    a: Annotated[int, Field(1)] = int(0)


assert Message(a=150).dumps() == b"\x08\x96\x01"
```

### Serialization into a [byte string](https://docs.python.org/3/library/stdtypes.html#bytes)

```python title="test_bytes.py"
from dataclasses import dataclass

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from typing_extensions import Annotated


@dataclass
class Message(BaseMessage):
    a: Annotated[int, Field(1)] = 0


message = Message(a=150)
assert bytes(message) == b"\x08\x96\x01"
```

### Deserialization from a [file object](https://docs.python.org/3/glossary.html#term-file-object)

```python title="test_read_from.py"
from dataclasses import dataclass

from pure_protobuf.annotations import Field
from pure_protobuf.message import BaseMessage
from typing_extensions import Annotated


@dataclass
class Message(BaseMessage):
    a: Annotated[int, Field(1)] = 0


assert Message.loads(b"\x08\x96\x01") == Message(a=150)
```
