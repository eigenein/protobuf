## `master`

- Add initial contribution guide.
- Add `Makefile`.
- Use `pytest`.
- Use `isort`.
- Remove `TypeMetadataType`. It is not a part of the standard, and I'd like to focus on maintaining compatibility with the reference implementation.
- Test snippets in `README.md`.

## `0.4.1`

- Added style checking with `flake8`.

## `0.4.0`

- Add packaging and publish to PyPI.

## `0.3.1`

- `encoding` module became `protobuf` module.
- Performance tests.
- `Bool.dump` 2.2 times faster.
- `Varint` 14% faster.
- `add_field` chaining.
- `__hash__` 17% faster.

## `0.3`

- README techniques added.
- Hashes of message types.
- Fixed: loading of missing required field doesn't raise `ValueError`.
- Message `load` doesn't use `StringIO` for reading embedded messages and packed repeated fields anymore.
- Add `TypeMetadata`
- Removed `MarshalableCode` (it's not `protobuf`'s business).
- Fixed: reading of `Int32` values raises `TypeError: 'str' object is not callable`

## `0.2`

- Fixed `Int32` type name (was `Int32Type`).
- Added validation of message type.
- `Unicode` type.
- Python code object type.
- Fixed casting values to `bool` and from `bool`.
