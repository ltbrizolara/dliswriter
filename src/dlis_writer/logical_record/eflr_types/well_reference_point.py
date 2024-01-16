from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import NumericAttribute, TextAttribute


class WellReferencePointItem(EFLRItem):
    """Model an object being part of WellReferencePoint EFLR."""

    parent: "WellReferencePointSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise WellReferencePointItem.

        Args:
            name        :   Name of the WellReferencePointItem.
            **kwargs    :   Values of to be set as characteristics of the WellReferencePointItem Attributes.
        """

        self.permanent_datum = TextAttribute('permanent_datum', parent_eflr=self)
        self.vertical_zero = TextAttribute('vertical_zero', parent_eflr=self)
        self.permanent_datum_elevation = NumericAttribute(
            'permanent_datum_elevation', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.above_permanent_datum = NumericAttribute(
            'above_permanent_datum', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.magnetic_declination = NumericAttribute(
            'magnetic_declination', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_1_name = TextAttribute('coordinate_1_name', parent_eflr=self)
        self.coordinate_1_value = NumericAttribute(
            'coordinate_1_value', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_2_name = TextAttribute('coordinate_2_name', parent_eflr=self)
        self.coordinate_2_value = NumericAttribute(
            'coordinate_2_value', representation_code=RepC.FDOUBL, parent_eflr=self)
        self.coordinate_3_name = TextAttribute('coordinate_3_name', parent_eflr=self)
        self.coordinate_3_value = NumericAttribute(
            'coordinate_3_value', representation_code=RepC.FDOUBL, parent_eflr=self)

        super().__init__(name, **kwargs)


class WellReferencePointSet(EFLRSet):
    """Model WellReferencePoint EFLR."""

    set_type = 'WELL-REFERENCE'
    logical_record_type = EFLRType.OLR
    item_type = WellReferencePointItem


WellReferencePointItem.parent_eflr_class = WellReferencePointSet
