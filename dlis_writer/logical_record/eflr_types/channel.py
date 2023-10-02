from typing import Union
from typing_extensions import Self

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import RepresentationCode, Units, LogicalRecordType


class Channel(EFLR):
    set_type = 'CHANNEL'
    logical_record_type = LogicalRecordType.CHANNL
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.long_name = self._create_attribute('long_name')
        self.properties = self._create_attribute('properties')
        self.representation_code = self._create_attribute('representation_code')
        self.units = self._create_attribute('units')
        self.dimension = self._create_attribute('dimension')
        self.axis = self._create_attribute('axis')
        self.element_limit = self._create_attribute('element_limit')
        self.source = self._create_attribute('source')
        self.minimum_value = self._create_attribute('minimum_value')
        self.maximum_value = self._create_attribute('maximum_value')

        self._dataset_name: str = None

    @property
    def key(self):
        return hash(type(self)), self.object_name

    @property
    def name(self):
        return self.object_name

    @property
    def dataset_name(self):
        return self._dataset_name if self._dataset_name is not None else self.name

    @dataset_name.setter
    def dataset_name(self, name: str):
        self._dataset_name = name

    @classmethod
    def create(cls, name: str, dimension: int = 1, long_name: str = None, repr_code: RepresentationCode = None,
               unit: Union[Units, str] = None, element_limit: int = None, dataset_name: str = None) -> Self:
        """

        Args:
            name:
            dimension:

            long_name:
            repr_code:
            unit:
            element_limit:

        Returns:
            channel:
        """

        channel = Channel(name)
        channel.long_name.value = long_name or name
        channel.representation_code.value = (repr_code if repr_code is not None else RepresentationCode.FDOUBL)
        channel.dimension.value = [dimension]
        channel.element_limit.value = [element_limit if element_limit is not None else dimension]

        channel.dataset_name = dataset_name

        if unit is not None:
            channel.units.value = unit

        return channel
