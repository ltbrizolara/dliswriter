import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.computation import Computation
from dlis_writer.logical_record.eflr_types.parameter import Parameter
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Process(EFLR):
    set_type = 'PROCESS'
    logical_record_type = LogicalRecordType.STATIC
    allowed_status = ('COMPLETE', 'ABORTED', 'IN-PROGRESS')

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.description = self._create_attribute('description', representation_code=RepC.ASCII)
        self.trademark_name = self._create_attribute('trademark_name', representation_code=RepC.ASCII)
        self.version = self._create_attribute('version', representation_code=RepC.ASCII)
        self.properties = self._create_attribute('properties', multivalued=True, representation_code=RepC.IDENT)
        self.status = self._create_attribute('status', converter=self.check_status, representation_code=RepC.IDENT)
        self.input_channels = self._create_attribute(
            'input_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.output_channels = self._create_attribute(
            'output_channels', multivalued=True, representation_code=RepC.OBNAME)
        self.input_computations = self._create_attribute(
            'input_computations', multivalued=True, representation_code=RepC.OBNAME)
        self.output_computations = self._create_attribute(
            'output_computations', multivalued=True, representation_code=RepC.OBNAME)
        self.parameters = self._create_attribute(
            'parameters', multivalued=True, representation_code=RepC.OBNAME)
        self.comments = self._create_attribute('comments', multivalued=True, representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)

    @classmethod
    def check_status(cls, status):
        if status not in cls.allowed_status:
            raise ValueError(f"'status' should be one of: {', '.join(cls.allowed_status)}; got {status}")
        return status

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'input_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'output_channels', Channel)
        obj.add_dependent_objects_from_config(config, 'input_computations', Computation)
        obj.add_dependent_objects_from_config(config, 'output_computations', Computation)
        obj.add_dependent_objects_from_config(config, 'parameters', Parameter)

        return obj
