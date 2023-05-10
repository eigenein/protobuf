# Migration from 2.x to 3.x

## Upgrade Python to 3.8 or above

Support for Python 3.7 is dropped.

## `#!python @message` decorator

The decorator has been removed. You should inherit your message classes from `#!python BaseMessage`.

## Fields

Replace annotations like `#!python foo: int = field(1)` with `#!python foo: Annotated[int, Field(1)]`.

## Integers

- Use the built-in `int` for variable-length integers, which use two's compliment negative representation.
- For ZigZag-encoded integers the new annotation `ZigZagInt` is introduced.

## Well-known types

`#!python typing.Any`, `#!python datetime.datetime`, and `#!python datetime.timedelta` are no longer mapped into the `.proto` types. Use `#!python pure_protobuf.well_known.Any_`, `#!python pure_protobuf.well_known.Timestamp`, and `#!python pure_protobuf.well_known.Duration` explicitly.

## `Anyof`

Replace `any_of` parameters with `#!python AnyOf` descriptors.
