"""Field annotations that may be used inside `Annotated`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NewType, Optional, Union

from pure_protobuf.exceptions import IncorrectAnnotationError
from pure_protobuf.helpers._dataclasses import DATACLASS_OPTIONS
from pure_protobuf.helpers._typing import DEFAULT, Sentinel

if TYPE_CHECKING:
    from pure_protobuf.one_of import OneOf


@dataclass(**DATACLASS_OPTIONS)
class Field:
    """Annotates a Protocol Buffers field."""

    number: int
    """
    Specifies the field's number.

    See also:
        - https://developers.google.com/protocol-buffers/docs/proto3#assigning_field_numbers
    """

    packed: Union[bool, Sentinel] = DEFAULT
    """Specifies whether the field should be packed in its serialized representation."""

    one_of: Optional["OneOf"] = None
    """Specifies a one-of group for this field."""

    @classmethod
    def _from_annotated_args(cls, *args: Any) -> Optional[Field]:
        """Extracts itself from the `Annotated[_, *args]` type hint, if present."""
        for arg in args:
            if isinstance(arg, Field):
                arg._validate()
                return arg
        return None

    def _validate(self) -> None:
        if not 1 <= self.number <= 536_870_911:
            raise IncorrectAnnotationError(
                f"field number {self.number} is outside the allowed range"
            )
        if 19000 <= self.number <= 19999:
            raise IncorrectAnnotationError(f"field number {self.number} is reserved")

    def _packed_or(self, default: bool) -> bool:
        return self.packed if isinstance(self.packed, bool) else default


double = NewType("double", float)
"""
Fixed 64-bit floating point.

See Also:
    - https://developers.google.com/protocol-buffers/docs/proto3#scalar
    - https://developers.google.com/protocol-buffers/docs/encoding#non-varint-nums
"""

fixed32 = NewType("fixed32", int)
"""
Fixed unsigned 32-bit integer.

See Also:
    - https://developers.google.com/protocol-buffers/docs/encoding#non-varint-nums
"""

fixed64 = NewType("fixed64", int)
"""
Fixed unsigned 64-bit integer.

See Also:
    - https://developers.google.com/protocol-buffers/docs/encoding#non-varint-nums
"""

sfixed32 = NewType("sfixed32", int)
"""
Fixed signed 32-bit integer.

See Also:
    - https://developers.google.com/protocol-buffers/docs/encoding#non-varint-nums
"""

sfixed64 = NewType("sfixed64", int)
"""
Fixed signed 64-bit integer.

See Also:
    - https://developers.google.com/protocol-buffers/docs/proto3#scalar
    - https://developers.google.com/protocol-buffers/docs/encoding#non-varint-nums
"""

# noinspection PyTypeChecker
uint = NewType("uint", int)
"""Unsigned variable-length integer."""
