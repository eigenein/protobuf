from typing import Any, Generic, List, MutableMapping, Tuple, Type

from typing_extensions import TypeVarTuple, Unpack

from pure_protobuf.message import BaseMessage

OneOfTs = TypeVarTuple("OneOfTs")


class OneOf(Generic[Unpack[OneOfTs]]):
    """
    See Also:
        - https://developers.google.com/protocol-buffers/docs/proto3#oneof.
    """

    __slots__ = ("_fields",)

    def __init__(self) -> None:
        self._fields: List[Tuple[int, str]] = []

    def _add_field(self, number: int, name: str) -> None:
        self._fields.append((number, name))

    def _keep_values(
        self,
        values: MutableMapping[str, Any],
        keep_number: int,
    ) -> None:
        for other_number, other_name in self._fields:
            if other_number != keep_number:
                values.pop(other_name, None)

    def _keep_attribute(self, message: BaseMessage, keep_number: int) -> None:
        for other_number, other_name in self._fields:
            if other_number != keep_number:
                super(BaseMessage, message).__setattr__(other_name, None)

    # FIXME: it actually returns `Union[None, Unpack[OneOfTs]]`, but that one just crashes Mypy (1.0.0).
    def __get__(self, instance: Any, type_: Type[Any]) -> Any:
        if not isinstance(instance, BaseMessage):
            # Allows passing the descriptor by reference, and we need to move the descriptor from
            # the corresponding annotation.
            # This is not a part of the public interface, hence the «type: ignore».
            return self  # type: ignore[return-value]
        for _, name in self._fields:
            value = getattr(instance, name)
            if value is not None:
                return value
        return None

    def __set__(self, instance: BaseMessage, _value: Any) -> None:
        raise RuntimeError("attempted to set the one-of field, use a specific attribute instead")

    # TODO: `which_one_of`.
