from typing import Any, List, MutableMapping, Tuple, Type

from pure_protobuf.message import BaseMessage


class OneOf:
    """
    See Also:
        - https://developers.google.com/protocol-buffers/docs/proto3#oneof
    """

    __slots__ = ("_fields",)

    def __init__(self):
        self._fields: List[Tuple[int, str]] = []

    def _add_field(self, number: int, name: str) -> None:
        self._fields.append((number, name))

    def _keep_values(
        self, type_: Type[BaseMessage], values: MutableMapping[str, Any], keep_number: int
    ) -> None:
        for other_number, other_name in self._fields:
            if other_number != keep_number:
                values.pop(other_name, None)

    def _keep_attribute(self, message: BaseMessage, keep_number: int) -> None:
        for other_number, other_name in self._fields:
            if other_number != keep_number:
                super(BaseMessage, message).__setattr__(other_name, None)

    def __get__(self, instance: Any, type_: Type[Any]) -> Any:
        if not isinstance(instance, BaseMessage):
            # Allows passing the descriptor by reference.
            return self
        for number, name in self._fields:
            value = getattr(instance, name)
            if value is not None:
                return value
        return None

    def __set__(self, instance: BaseMessage, _value: Any) -> None:
        raise RuntimeError("attempted to set the one-of field, use a specific attribute instead")

    # TODO: `which_one_of`.
