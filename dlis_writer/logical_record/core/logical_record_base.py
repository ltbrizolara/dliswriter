from abc import abstractmethod


class LogicalRecordBase:
    """Base for all logical record classes."""

    set_type: str = NotImplemented

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @property
    def key(self):
        return hash(type(self))

    @abstractmethod
    def represent_as_bytes(self) -> bytes:
        pass

