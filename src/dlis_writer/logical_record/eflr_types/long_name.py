from dlis_writer.logical_record.core.eflr import EFLRTable, EFLRItem
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class LongNameItem(EFLRItem):
    """Model an object being part of LongName EFLR."""

    parent: "LongNameTable"

    def __init__(self, name: str, **kwargs):
        """Initialise LongNameItem.

        Args:
            name        :   Name of the LongNameItem.
            **kwargs    :   Values of to be set as characteristics of the LongNameItem Attributes.
        """

        self.general_modifier = Attribute(
            'general_modifier', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.quantity = Attribute('quantity', representation_code=RepC.ASCII, parent_eflr=self)
        self.quantity_modifier = Attribute(
            'quantity_modifier', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.altered_form = Attribute('altered_form', representation_code=RepC.ASCII, parent_eflr=self)
        self.entity = Attribute('entity', representation_code=RepC.ASCII, parent_eflr=self)
        self.entity_modifier = Attribute(
            'entity_modifier', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.entity_number = Attribute('entity_number', representation_code=RepC.ASCII, parent_eflr=self)
        self.entity_part = Attribute('entity_part', representation_code=RepC.ASCII, parent_eflr=self)
        self.entity_part_number = Attribute('entity_part_number', representation_code=RepC.ASCII, parent_eflr=self)
        self.generic_source = Attribute('generic_source', representation_code=RepC.ASCII, parent_eflr=self)
        self.source_part = Attribute('source_part', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.source_part_number = Attribute(
            'source_part_number', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.conditions = Attribute('conditions', representation_code=RepC.ASCII, multivalued=True, parent_eflr=self)
        self.standard_symbol = Attribute('standard_symbol', representation_code=RepC.ASCII, parent_eflr=self)
        self.private_symbol = Attribute('private_symbol', representation_code=RepC.ASCII, parent_eflr=self)

        super().__init__(name, **kwargs)


class LongNameTable(EFLRTable):
    """Model LongName EFLR."""

    set_type = 'LONG-NAME'
    logical_record_type = EFLRType.LNAME
    item_type = LongNameItem


LongNameItem.parent_eflr_class = LongNameTable
