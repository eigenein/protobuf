from typing import Callable, Generic, Iterator, TypeVar

from typing_extensions import ParamSpec

from pure_protobuf.interfaces._repr import ReprWithInner

P = ParamSpec("P")
R = TypeVar("R")


class ReadCallback(ReprWithInner, Generic[P, R]):
    __slots__ = ("inner",)

    # noinspection PyProtocol
    inner: Callable[P, R]

    def __init__(self, inner: Callable[P, R]):
        self.inner = inner

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Iterator[R]:
        yield self.inner(*args, **kwargs)
