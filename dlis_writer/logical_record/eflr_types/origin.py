from datetime import datetime
import logging

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute, ListAttribute, DTimeAttribute, NumericAttribute


logger = logging.getLogger(__name__)


class Origin(EFLR):
    set_type = 'ORIGIN'
    logical_record_type = LogicalRecordType.OLR

    def __init__(self, name: str, set_name: str = None, **kwargs):

        super().__init__(name, set_name)

        self.file_id = Attribute('file_id', representation_code=RepC.ASCII)
        self.file_set_name = Attribute('file_set_name', representation_code=RepC.IDENT)
        self.file_set_number = NumericAttribute('file_set_number', representation_code=RepC.UVARI)
        self.file_number = NumericAttribute('file_number', representation_code=RepC.UVARI)
        self.file_type = Attribute('file_type', representation_code=RepC.IDENT)
        self.product = Attribute('product', representation_code=RepC.ASCII)
        self.version = Attribute('version', representation_code=RepC.ASCII)
        self.programs = ListAttribute('programs', representation_code=RepC.ASCII)
        self.creation_time = DTimeAttribute('creation_time')
        self.order_number = Attribute('order_number', representation_code=RepC.ASCII)
        self.descent_number = NumericAttribute('descent_number', representation_code=RepC.UNORM)
        self.run_number = NumericAttribute('run_number', representation_code=RepC.UNORM)
        self.well_id = NumericAttribute('well_id', representation_code=RepC.UNORM)
        self.well_name = Attribute('well_name', representation_code=RepC.ASCII)
        self.field_name = Attribute('field_name', representation_code=RepC.ASCII)
        self.producer_code = NumericAttribute('producer_code', representation_code=RepC.UNORM)
        self.producer_name = Attribute('producer_name', representation_code=RepC.ASCII)
        self.company = Attribute('company', representation_code=RepC.ASCII)
        self.name_space_name = Attribute('name_space_name', representation_code=RepC.IDENT)
        self.name_space_version = NumericAttribute('name_space_version', representation_code=RepC.UVARI)

        if "creation_time" not in kwargs:
            logger.info("Creation time ('creation_time') not specified; setting it to the current date and time")
            kwargs["creation_time"] = datetime.now()

        self.set_attributes(**kwargs)
