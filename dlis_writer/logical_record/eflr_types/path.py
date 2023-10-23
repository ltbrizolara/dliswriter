import logging
from typing_extensions import Self
from configparser import ConfigParser

from dlis_writer.logical_record.core import EFLR
from dlis_writer.logical_record.eflr_types.frame import Frame
from dlis_writer.logical_record.eflr_types.channel import Channel
from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePoint
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC


logger = logging.getLogger(__name__)


class Path(EFLR):
    set_type = 'PATH'
    logical_record_type = LogicalRecordType.FRAME

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.frame_type = self._create_attribute('frame_type', representation_code=RepC.OBNAME)
        self.well_reference_point = self._create_attribute('well_reference_point', representation_code=RepC.OBNAME)
        self.value = self._create_attribute('value', multivalued=True, representation_code=RepC.OBNAME)
        self.borehole_depth = self._create_attribute('borehole_depth', converter=float)
        self.vertical_depth = self._create_attribute('vertical_depth', converter=float)
        self.radial_drift = self._create_attribute('radial_drift', converter=float)
        self.angular_drift = self._create_attribute('angular_drift', converter=float)
        self.time = self._create_attribute('time', converter=float)
        self.depth_offset = self._create_attribute('depth_offset', converter=float)
        self.measure_point_offset = self._create_attribute('measure_point_offset', converter=float)
        self.tool_zero_offset = self._create_attribute('tool_zero_offset', converter=float)

        self.set_attributes(**kwargs)

    @classmethod
    def make_from_config(cls, config: ConfigParser, key=None) -> Self:
        obj: Self = super().make_from_config(config, key=key)

        obj.add_dependent_objects_from_config(config, 'frame_type', Frame, single=True)
        obj.add_dependent_objects_from_config(config, 'well_reference_point', WellReferencePoint, single=True)
        obj.add_dependent_objects_from_config(config, 'value', Channel)

        return obj

