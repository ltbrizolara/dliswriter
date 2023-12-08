from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute


class AxisItem(EFLRItem):
    """Model an object being part of Axis EFLR."""

    parent: "AxisTable"

    def __init__(self, name: str, **kwargs):
        """Initialise AxisObject.

        Args:
            name        :   Name of the AxisObject.
            **kwargs    :   Values of to be set as characteristics of the AxisObject Attributes.
        """

        self.axis_id = Attribute('axis_id', representation_code=RepC.IDENT, parent_eflr=self)
        self.coordinates = Attribute('coordinates', multivalued=True, parent_eflr=self,
                                     converter=self.convert_maybe_numeric)
        self.spacing = NumericAttribute('spacing', parent_eflr=self)

        super().__init__(name, **kwargs)


class AxisTable(EFLRTable):
    """Model Axis EFLR."""

    set_type = 'AXIS'
    logical_record_type = EFLRType.AXIS
    item_type = AxisItem


AxisItem.parent_eflr_class = AxisTable
