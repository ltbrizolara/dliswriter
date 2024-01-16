import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.logical_record.eflr_types.equipment import EquipmentSet
from dlis_writer.logical_record.eflr_types.channel import ChannelSet
from dlis_writer.logical_record.eflr_types.parameter import ParameterSet
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import EFLRAttribute, StatusAttribute, TextAttribute


logger = logging.getLogger(__name__)


class ToolItem(EFLRItem):
    """Model an object being part of Tool EFLR."""

    parent: "ToolSet"

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise ToolItem.

        Args:
            name        :   Name of the ToolItem.
            **kwargs    :   Values of to be set as characteristics of the ToolItem Attributes.
        """

        self.description = TextAttribute('description', parent_eflr=self)
        self.trademark_name = TextAttribute('trademark_name', parent_eflr=self)
        self.generic_name = TextAttribute('generic_name', parent_eflr=self)
        self.parts = EFLRAttribute('parts', object_class=EquipmentSet, multivalued=True, parent_eflr=self)
        self.status = StatusAttribute('status', parent_eflr=self)
        self.channels = EFLRAttribute('channels', object_class=ChannelSet, multivalued=True, parent_eflr=self)
        self.parameters = EFLRAttribute('parameters', object_class=ParameterSet, multivalued=True, parent_eflr=self)

        super().__init__(name, **kwargs)


class ToolSet(EFLRSet):
    """Model Tool EFLR."""

    set_type = 'TOOL'
    logical_record_type = EFLRType.STATIC
    item_type = ToolItem


ToolItem.parent_eflr_class = ToolSet
