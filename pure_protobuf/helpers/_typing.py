from collections.abc import Iterable
from typing import Any, List, Tuple, Union

from typing_extensions import TypeGuard, get_args, get_origin

try:
    from types import NoneType  # type: ignore
except ImportError:
    NoneType = type(None)  # type: ignore


class Sentinel:  # pragma: no cover
    """Sentinel object used for defaults."""

    def __str__(self) -> str:  # pragma: no cover
        return "DEFAULT"

    def __repr__(self) -> str:  # pragma: no cover
        return "DEFAULT"


DEFAULT = Sentinel()


def extract_repeated(hint: Any) -> Tuple[Any, TypeGuard[List]]:
    """Extract a possible repeated flag."""
    origin = get_origin(hint)
    if isinstance(origin, type) and (origin is Iterable or issubclass(origin, list)):
        return get_args(hint)[0], True
    return hint, False


def extract_optional(hint: Any) -> Tuple[Any, bool]:
    """Extract a possible optional flag."""
    if get_origin(hint) is Union:
        cleaned_args = tuple(arg for arg in get_args(hint) if arg is not NoneType)
        return Union[cleaned_args], True
    return hint, False
