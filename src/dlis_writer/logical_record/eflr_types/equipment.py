from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, NumericAttribute, StatusAttribute, TextAttribute


class EquipmentItem(EFLRItem):
    """Model an object being part of Equipment EFLR."""

    parent: "EquipmentSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise EquipmentItem.

        Args:
            name        :   Name of the EquipmentItem.
            **kwargs    :   Values of to be set as characteristics of the EquipmentItem Attributes.
        """

        self.trademark_name = TextAttribute('trademark_name', parent_eflr=self)
        self.status = StatusAttribute('status', parent_eflr=self)
        self._type = Attribute('_type', representation_code=RepC.IDENT, parent_eflr=self)
        self.serial_number = Attribute('serial_number', representation_code=RepC.IDENT, parent_eflr=self)
        self.location = Attribute('location', representation_code=RepC.IDENT, parent_eflr=self)
        self.height = NumericAttribute('height', parent_eflr=self)
        self.length = NumericAttribute('length', parent_eflr=self)
        self.minimum_diameter = NumericAttribute('minimum_diameter', parent_eflr=self)
        self.maximum_diameter = NumericAttribute('maximum_diameter', parent_eflr=self)
        self.volume = NumericAttribute('volume', parent_eflr=self)
        self.weight = NumericAttribute('weight', parent_eflr=self)
        self.hole_size = NumericAttribute('hole_size', parent_eflr=self)
        self.pressure = NumericAttribute('pressure', parent_eflr=self)
        self.temperature = NumericAttribute('temperature', parent_eflr=self)
        self.vertical_depth = NumericAttribute('vertical_depth', parent_eflr=self)
        self.radial_drift = NumericAttribute('radial_drift', parent_eflr=self)
        self.angular_drift = NumericAttribute('angular_drift', parent_eflr=self)

        super().__init__(name, **kwargs)


class EquipmentSet(EFLRSet):
    """Model Equipment EFLR."""

    set_type = 'EQUIPMENT'
    logical_record_type = EFLRType.STATIC
    item_type = EquipmentItem


EquipmentItem.parent_eflr_class = EquipmentSet
