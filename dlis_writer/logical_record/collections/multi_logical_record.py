from abc import abstractmethod

from dlis_writer.logical_record.core.logical_record_base import LogicalRecordBase


class MultiLogicalRecord:
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def set_origin_reference(self, value):
        pass


class SingleLogicalRecordWrapper(MultiLogicalRecord):
    def __init__(self, lr: LogicalRecordBase):
        super().__init__()
        self.lr = lr

    def __len__(self):
        return 1

    def __iter__(self):
        return iter((self.lr,))

    def set_origin_reference(self, value):
        self.lr.origin_reference = value
