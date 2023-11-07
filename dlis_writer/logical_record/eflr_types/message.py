from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, DTimeAttribute, NumericAttribute


class Message(EFLR):
    set_type = 'MESSAGE'
    logical_record_type = EFLRType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self._type = Attribute('_type', representation_code=RepC.IDENT)
        self.time = DTimeAttribute('time', allow_float=True)
        self.borehole_drift = NumericAttribute('borehole_drift')
        self.vertical_depth = NumericAttribute('vertical_depth')
        self.radial_drift = NumericAttribute('radial_drift')
        self.angular_drift = NumericAttribute('angular_drift')
        self.text = Attribute('text', representation_code=RepC.ASCII, multivalued=True)

        self.set_attributes(**kwargs)


class Comment(EFLR):
    set_type = 'COMMENT'
    logical_record_type = EFLRType.SCRIPT

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.text = Attribute('text', representation_code=RepC.ASCII, multivalued=True)

        self.set_attributes(**kwargs)
