# Overview

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/eigenein/protobuf/check.yml?label=checks)](https://github.com/eigenein/protobuf/actions/workflows/check.yml)
[![Code coverage](https://codecov.io/gh/eigenein/protobuf/branch/master/graph/badge.svg?token=bJarwbLlY7)](https://codecov.io/gh/eigenein/protobuf)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pure-protobuf.svg)](https://pypistats.org/packages/pure-protobuf)
[![PyPI – Version](https://img.shields.io/pypi/v/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/pure-protobuf.svg)](https://pypi.org/project/pure-protobuf/#files)
[![License](https://img.shields.io/pypi/l/pure-protobuf.svg)](https://github.com/eigenein/protobuf/blob/master/LICENSE)

!!! tip "Tip"

    The code snippets in this documentation are automatically tested and should work «as is».

## Quick examples

=== "With dataclasses"

    ```python title="dataclass_example.py"
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
    
    
    request = SearchRequest(
        query="hello",
        page_number=uint(1),
        result_per_page=uint(10),
    )
    buffer = bytes(request)
    assert buffer == b"\x0A\x05hello\x10\x01\x18\x0A"
    assert SearchRequest.read_from(BytesIO(buffer))
    ```

=== "With pydantic"

    ```python title="pydantic_example.py"
    from io import BytesIO
    
    from pure_protobuf.annotations import Field, uint
    from pure_protobuf.message import BaseMessage
    from pydantic import BaseModel
    from typing_extensions import Annotated
    
    
    class SearchRequest(BaseMessage, BaseModel):
        query: Annotated[str, Field(1)] = ""
        page_number: Annotated[uint, Field(2)] = 0
        result_per_page: Annotated[uint, Field(3)] = 0
    
    
    request = SearchRequest(
        query="hello",
        page_number=uint(1),
        result_per_page=uint(10),
    )
    buffer = bytes(request)
    assert buffer == b"\x0A\x05hello\x10\x01\x18\x0A"
    assert SearchRequest.read_from(BytesIO(buffer))
    ```

!!! info "Prerequisite"

    `#!python BaseMessage` requires a subclass to accept field values via keyword parameters in its `#!python __init__()` method. For most cases, one should use something like the built-in [`#!python dataclasses`](https://docs.python.org/3/library/dataclasses.html) or a third-party package like [`#!python pydantic`](https://docs.pydantic.dev/). But it is certainly possible to go a «vanilla» way:

    ```python title="test_vanilla.py"
    from io import BytesIO
    
    from pure_protobuf.annotations import Field, uint
    from pure_protobuf.message import BaseMessage
    from typing_extensions import Annotated
    

    class Message(BaseMessage):
        a: Annotated[uint, Field(1)] = uint(0)

        def __init__(self, a: uint) -> None:
            self.a = a

    
    assert Message.read_from(BytesIO(b"\x08\x96\x01")).a == uint(150)
    ```
