from sys import version_info
from typing import TYPE_CHECKING, Callable, TypeVar

_T = TypeVar("_T")


if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    import dataclasses

    def dataclass(*, frozen: bool = False, kw_only: bool = False, slots: bool = False) -> Callable[[_T], _T]:
        options_3_10 = {}
        if version_info >= (3, 10):
            options_3_10["slots"] = slots
        return dataclasses.dataclass(frozen=frozen, kw_only=kw_only, **options_3_10)
