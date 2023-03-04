# Migration from 2.x to 3.x

## `#!python @message` decorator

The decorator has been removed. You should inherit your message classes from `#!python BaseMessage`.

## Fields

Replace annotations like `#!python foo: int = field(1)` with `#!python foo: Annotated[int, Field(1)]`.

## Serialization and deserialization

Replace:

- `#!python message.dumps()` with `#!python bytes(message)` or `#!python message.write_to(…)`
- `#!python loads()` with `#!python read_from(BytesIO(…))`

## Well-known types

`#!python typing.Any`, `#!python datetime.datetime`, and `#!python datetime.timedelta` are no longer mapped into the `.proto` types. Use `#!python pure_protobuf.well_known.Any_`, `#!python pure_protobuf.well_known.Timestamp`, and `#!python pure_protobuf.well_known.Duration` explicitly.

## `Anyof`

Replace `any_of` parameters with `#!python AnyOf` descriptors.
