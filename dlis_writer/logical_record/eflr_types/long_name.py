from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import EFLRType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class LongName(EFLR):
    set_type = 'LONG-NAME'
    logical_record_type = EFLRType.LNAME

    def __init__(self, name: str, set_name: str = None, **kwargs):
        super().__init__(name, set_name)

        self.general_modifier = Attribute('general_modifier', representation_code=RepC.ASCII, multivalued=True)
        self.quantity = Attribute('quantity', representation_code=RepC.ASCII)
        self.quantity_modifier = Attribute('quantity_modifier', representation_code=RepC.ASCII, multivalued=True)
        self.altered_form = Attribute('altered_form', representation_code=RepC.ASCII)
        self.entity = Attribute('entity', representation_code=RepC.ASCII)
        self.entity_modifier = Attribute('entity_modifier', representation_code=RepC.ASCII, multivalued=True)
        self.entity_number = Attribute('entity_number', representation_code=RepC.ASCII)
        self.entity_part = Attribute('entity_part', representation_code=RepC.ASCII)
        self.entity_part_number = Attribute('entity_part_number', representation_code=RepC.ASCII)
        self.generic_source = Attribute('generic_source', representation_code=RepC.ASCII)
        self.source_part = Attribute('source_part', representation_code=RepC.ASCII, multivalued=True)
        self.source_part_number = Attribute('source_part_number', representation_code=RepC.ASCII, multivalued=True)
        self.conditions = Attribute('conditions', representation_code=RepC.ASCII, multivalued=True)
        self.standard_symbol = Attribute('standard_symbol', representation_code=RepC.ASCII)
        self.private_symbol = Attribute('private_symbol', representation_code=RepC.ASCII)

        self.set_attributes(**kwargs)
