from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType


class Path(EFLR):
    set_type = 'PATH'
    logical_record_type = LogicalRecordType.FRAME
    lr_type_struct = EFLR.make_lr_type_struct(logical_record_type)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.frame_type = self._create_attribute('frame_type')
        self.well_reference_point = self._create_attribute('well_reference_point')
        self.value = self._create_attribute('value')
        self.borehole_depth = self._create_attribute('borehole_depth')
        self.vertical_depth = self._create_attribute('vertical_depth')
        self.radial_drift = self._create_attribute('radial_drift')
        self.angular_drift = self._create_attribute('angular_drift')
        self.time = self._create_attribute('time')
        self.depth_offset = self._create_attribute('depth_offset')
        self.measure_point_offset = self._create_attribute('measure_point_offset')
        self.tool_zero_offset = self._create_attribute('tool_zero_offset')
