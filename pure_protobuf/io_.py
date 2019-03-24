"""
`pure-protobuf` contributors © 2011-2019
"""

from abc import ABC, abstractmethod
from io import BytesIO
from typing import Any, BinaryIO, Union

# Type hinting doesn't recognize `BytesIO` as an instance of `BinaryIO`.
IO = Union[BinaryIO, BytesIO]


class Dumps(ABC):
    @abstractmethod
    def dump(self, value: Any, io: IO):
        """
        Serializes a value into a file-like object.
        """
        raise NotImplementedError()

    def dumps(self, value: Any) -> bytes:
        """
        Serializes a value into a byte string
        """
        with BytesIO() as io:
            self.dump(value, io)
            return io.getvalue()


class Loads(ABC):
    @abstractmethod
    def load(self, io: IO) -> Any:
        """
        Deserializes a value from a file-like object.
        """
        raise NotImplementedError()

    def loads(self, bytes_: bytes) -> Any:
        """
        Deserializes a value from a byte string.
        """
        with BytesIO(bytes_) as io:
            return self.load(io)
