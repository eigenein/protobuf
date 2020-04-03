## `master`

- Chore: refactor Google type serializers registration
- Chore: #27 integrate mypy checks, fix some of mypy errors
- Chore: exclude every test package when installing by @shibotto

## `2.0.0`

- Break: drop Python 2.x and 3.5 support and remove the legacy interface #59

## `1.2.0`

- New: #63 convenience method for an optional field

## `1.1.0`

- New: #34 support `google.protobuf.Duration`
- New: #26 support [`google.protobuf.Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)
- New: #56 provide public API for reading and writing `VarInt`s
- Chore: #40 move Google well-known types out to a separate namespace

## `1.0.1`

- Fix: #46 accept a bytes-like object as a byte-string field value

## `1.0.0`

- **New**: dataclasses interface for defining types using [Python type hinting](https://www.python.org/dev/peps/pep-0484/)
- **Change**: legacy interface is available via `pure_protobuf.legacy`

## `0.5.0`

- Chore: add initial contribution guide
- Chore: add `Makefile`
- Chore: #2 use `pytest`
- Chore: use `isort`
- **Change**: Remove `TypeMetadataType`. It is not a part of the standard, and I'd like to focus on maintaining compatibility with the reference implementation
- Chore: #2 test snippets in `README.md`
- **Change**: drop `Message.__delattr__` support
- New: #6 add Python 3 support
- Change: change license to MIT

## `0.4.1`

- Chore: #4 added style checking with `flake8`

## `0.4.0`

- New: #5 add packaging and publish to PyPI

## `0.3.1`

- Change: `encoding` module became `protobuf` module
- Chore: performance tests
- Opt: `Bool.dump` 2.2 times faster
- Opt: `Varint` 14% faster
- New: `add_field` chaining
- Opt: `__hash__` 17% faster

## `0.3`

- Chore: README techniques added
- New: hashes of message types
- Fix: loading of missing required field doesn't raise `ValueError`
- Chore: message `load` doesn't use `StringIO` for reading embedded messages and packed repeated fields anymore
- New: add `TypeMetadata`
- Change: remove `MarshalableCode` (it's not `protobuf`'s business)
- Fix: reading of `Int32` values raises `TypeError: 'str' object is not callable`

## `0.2`

- Fix: `Int32` type name (was `Int32Type`)
- New: add validation of message type
- New: `Unicode` type
- New: Python code object type
- Fix: casting values to `bool` and from `bool`
