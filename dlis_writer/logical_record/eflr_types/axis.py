from dlis_writer.logical_record.core.eflr import EFLR, EFLRObject
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class AxisObject(EFLRObject):

    def __init__(self, name: str, parent: "Axis", **kwargs):

        self.axis_id = Attribute('axis_id', representation_code=RepC.IDENT, parent_eflr=self)
        self.coordinates = NumericAttribute('coordinates', multivalued=True, parent_eflr=self)
        self.spacing = NumericAttribute('spacing', parent_eflr=self)

        super().__init__(name, parent, **kwargs)


class Axis(EFLR):
    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    object_type = AxisObject

