## `2.2.1`

- Fix: implement two's compliment varint encoding for `int32` and `int64` #103

## `2.2.0`

- Opt: publish to PyPI from GitHub Actionsπ
- Opt: apply `black` formatting
- Opt: move project configuration to `pyproject.toml`
- Break: drop Python 3.6 support as it's reached the end-of-life phase of its release cycle (@eigenein)

## `2.1.0`

- New: support for `field(..., packed=False)` to serialize unpacked repeated fields #90 (@d70-t)

## `2.0.1`

- Fix: F541 f-string is missing placeholders
- Chore: refactor Google type serializers registration
- Chore: integrate mypy checks, fix some of mypy errors #27
- Chore: exclude every test package when installing (@shibotto)

## `2.0.0`

- Break: drop Python 2.x and 3.5 support and remove the legacy interface #59

## `1.2.0`

- New: convenience method for an optional field #63

## `1.1.0`

- New: support `google.protobuf.Duration` #34
- New: support [`google.protobuf.Any`](https://developers.google.com/protocol-buffers/docs/proto3#any)  #26
- New: provide public API for reading and writing `VarInt`s #56
- Chore: move Google well-known types out to a separate namespace #40

## `1.0.1`

- Fix: accept a bytes-like object as a byte-string field value #46

## `1.0.0`

- New: dataclasses interface for defining types using [Python type hinting](https://www.python.org/dev/peps/pep-0484/)
- Break: legacy interface is available via `pure_protobuf.legacy`

## `0.5.0`

- Chore: add initial contribution guide
- Chore: add `Makefile`
- Chore: use `pytest` #2
- Chore: use `isort`
- Break: Remove `TypeMetadataType`. It is not a part of the standard, and I'd like to focus on maintaining compatibility with the reference implementation
- Chore: test snippets in `README.md` #2
- Break: drop `Message.__delattr__` support
- New: add Python 3 support #6
- Break: change the license to MIT

## `0.4.1`

- Chore: added style checking with `flake8` #4

## `0.4.0`

- New: add packaging and publish to PyPI #5

## `0.3.1`

- Break: rename `encoding` module to `protobuf`
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

- Break: `Int32` type name (was `Int32Type`)
- New: add validation of message type
- New: `Unicode` type
- New: Python code object type
- Fix: casting values to `bool` and from `bool`
