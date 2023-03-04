from sys import version_info
from typing import TYPE_CHECKING, Callable, Type, TypeVar, overload

_T = TypeVar("_T")


if TYPE_CHECKING:
    from dataclasses import dataclass
else:
    import dataclasses

    @overload
    def dataclass(frozen: bool = False, kw_only: bool = False, slots: bool = False) -> Callable[[_T], _T]:
        ...

    @overload
    def dataclass(cls: Type[_T]) -> Type[_T]:
        ...

    def dataclass(
        cls=None,
        /,
        *,
        frozen=False,
        kw_only=False,
        slots=False,
    ):
        options_3_10 = {}
        if version_info >= (3, 10):
            options_3_10["slots"] = slots
            options_3_10["kw_only"] = kw_only
        return dataclasses.dataclass(cls, frozen=frozen, **options_3_10)
