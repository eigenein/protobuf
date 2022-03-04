import dataclasses
from enum import Enum
from typing import Any, Optional, Tuple


@dataclasses.dataclass(frozen=True)
class OneOfPartInfo:
    name: str
    type_: type
    number: int


class _OneOfAttrs(Enum):
    SET_VALUE = "__set_value__"
    PARTS = "__parts__"
    FIELDS = "__fields__"


def scheme(obj: 'OneOf_') -> Tuple[OneOfPartInfo, ...]:
    return getattr(obj, _OneOfAttrs.PARTS.value)


class OneOf_:
    """
    Defines an oneof field.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#oneof
    """
    def __init__(self, *parts: OneOfPartInfo):
        # ugly sets to get round custom setattr
        super().__setattr__(_OneOfAttrs.FIELDS.value, frozenset(part.name for part in parts))
        super().__setattr__(_OneOfAttrs.PARTS.value, parts)
        super().__setattr__(_OneOfAttrs.SET_VALUE.value, None)

    def __getattr__(self, name):
        if name not in getattr(self, _OneOfAttrs.FIELDS.value):
            raise AttributeError(f"Field {name} is not found")

        set_value = getattr(self, _OneOfAttrs.SET_VALUE.value)
        if set_value is not None:
            field_name, real_value = set_value
            if field_name == name:
                return real_value

        return None

    def __setattr__(self, name, value):
        if name not in getattr(self, _OneOfAttrs.FIELDS.value):
            raise AttributeError(f"Field {name} is not found")

        super().__setattr__(_OneOfAttrs.SET_VALUE.value, (name, value))

    @property
    def which_one_of(self) -> Optional[str]:
        set_value = getattr(self, _OneOfAttrs.SET_VALUE.value)
        if set_value is None:
            return None

        field_name, _ = set_value
        return field_name

    @property
    def __internals(self) -> Tuple[Any, Any, Any]:
        return (getattr(self, _OneOfAttrs.FIELDS.value),
                getattr(self, _OneOfAttrs.PARTS.value),
                getattr(self, _OneOfAttrs.SET_VALUE.value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OneOf_):
            return NotImplemented

        return self.__internals == other.__internals

    def __hash__(self) -> int:
        return hash(self.__internals)

    # for debug purposes I guess
    def __repr__(self) -> str:
        fields, parts, set_value = self.__internals
        return (f"{fields} \n"
                f"set: {parts} \n"
                f"parts: {set_value}")
