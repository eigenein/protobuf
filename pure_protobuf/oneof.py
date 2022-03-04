import dataclasses
from typing import Any, Optional


@dataclasses.dataclass(frozen=True)
class OneOfPartInfo:
    name: str
    type_: type
    number: int


class OneOf_:
    """
    Defines an oneof field.
    See also: https://developers.google.com/protocol-buffers/docs/proto3#oneof
    """
    def __init__(self, *parts: OneOfPartInfo):
        # ugly sets to get round custom setattr
        # fields created as tuple on purposes
        super().__setattr__('fields', tuple(part.name for part in parts))
        super().__setattr__('parts', parts)
        super().__setattr__('set_value', None)

    def __getattr__(self, name):
        if name not in self.fields:
            raise AttributeError(f"Field {name} is not found")

        if self.set_value is not None:
            field_name, value = self.set_value
            if field_name == name:
                return value

        return None

    def __setattr__(self, name, value):
        if name not in self.fields:
            raise AttributeError(f"Field {name} is not found")

        super().__setattr__('set_value', (name, value))

    @property
    def which_one_of(self) -> Optional[str]:
        if self.set_value is None:
            return None

        field_name, _ = self.set_value
        return field_name

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, OneOf_) and \
            other.fields == self.fields and \
            other.parts == self.parts and \
            other.set_value == self.set_value

    def __hash__(self) -> int:
        return hash((self.fields, self.parts, self.set_value))

    # for debug purposes I guess
    def __repr__(self) -> str:
        return (f"{self.fields} \n"
                f"set: {self.parts} \n"
                f"parts: {self.set_value}")
