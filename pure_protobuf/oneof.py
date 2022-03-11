import dataclasses
import functools
from enum import Enum
from typing import Any, Callable, Optional, Tuple


@dataclasses.dataclass(frozen=True)
class OneOfPartInfo:
    name: str
    type_: type
    number: int
    packed: bool = True


class _OneOfAttrs(Enum):
    SET_VALUE = "__set_value__"
    PARTS = "__parts__"
    FIELDS = "__fields__"


def scheme(obj: 'OneOf_') -> Tuple[OneOfPartInfo, ...]:
    return obj.__parts__


def _internals(self) -> Tuple[Any, Any, Any]:
    return (self.__fields__, self.__parts__, self.__set_value__)


def _name_in_attrs_check(func: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore
    @functools.wraps(func)
    def inner(self, name, *args):
        if name not in self.__fields__:
            raise AttributeError(f"Field {name} is not found")
        return func(self, name, *args)
    return inner


class OneOf_:
    """
    Defines an oneof field.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#oneof
    """
    def __init__(self, scheme_: Tuple[OneOfPartInfo, ...]):
        # ugly sets to get round custom setattr
        super().__setattr__(_OneOfAttrs.FIELDS.value, frozenset(part.name for part in scheme_))
        super().__setattr__(_OneOfAttrs.PARTS.value, scheme_)
        super().__setattr__(_OneOfAttrs.SET_VALUE.value, None)

    @_name_in_attrs_check
    def __getattr__(self, name):
        if self.which_one_of == name:
            _, value = self.__set_value__
            return value

        return None

    @_name_in_attrs_check
    def __delattr__(self, name):
        if self.which_one_of == name:
            return super().__setattr__(_OneOfAttrs.SET_VALUE.value, None)

        raise AttributeError(f"Field {name} is not set, "
                             f"{self.which_one_of} is set")

    @_name_in_attrs_check
    def __setattr__(self, name, value):
        super().__setattr__(_OneOfAttrs.SET_VALUE.value, (name, value))

    @property
    def which_one_of(self) -> Optional[str]:
        set_value = self.__set_value__
        if set_value is None:
            return None

        field_name, _ = set_value
        return field_name

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OneOf_):
            return NotImplemented

        return _internals(self) == _internals(other)

    def __hash__(self) -> int:
        return hash(_internals(self))

    # for debug purposes I guess
    def __repr__(self) -> str:
        fields, parts, set_value = _internals(self)
        return (f"{fields} \n"
                f"parts: {parts} \n"
                f"set: {set_value}")
