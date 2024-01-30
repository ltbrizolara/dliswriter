import logging
from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRItem, EFLRSet
from dlis_writer.logical_record.eflr_types.axis import AxisSet
from dlis_writer.logical_record.eflr_types.zone import ZoneSet
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import (EFLRAttribute, NumericAttribute, DimensionAttribute,
                                                       TextAttribute, IdentAttribute)


logger = logging.getLogger(__name__)


class ComputationItem(EFLRItem):
    """Model an object being part of Computation EFLR."""

    parent: "ComputationSet"

    def __init__(self, name: str, parent: "ComputationSet", **kwargs: Any) -> None:
        """Initialise ComputationItem.

        Args:
            name            :   Name of the ComputationItem.
            parent          :   Parent ComputationSet of this ComputationItem.
            **kwargs        :   Values of to be set as characteristics of the ComputationItem Attributes.
        """

        self.long_name = TextAttribute('long_name')
        self.properties = IdentAttribute('properties', multivalued=True, converter=self.convert_property)
        self.dimension = DimensionAttribute('dimension')
        self.axis = EFLRAttribute('axis', object_class=AxisSet)
        self.zones = EFLRAttribute('zones', object_class=ZoneSet, multivalued=True)
        self.values = NumericAttribute('values', multivalued=True)
        self.source = EFLRAttribute('source')

        super().__init__(name, parent=parent, **kwargs)

        self.check_values_and_zones()

    def _set_defaults(self) -> None:
        """Set up default values of ComputationItem parameters if not explicitly set previously."""

        if not self.dimension.value:
            logger.debug(f"Setting dimension of '{self}' to the default value: [1]")
            self.dimension.value = [1]

    def check_values_and_zones(self) -> None:
        """Check that the currently set values and zones attributes match in sizes."""

        if self.values.value is not None and self.zones.value is not None:
            if (nv := len(self.values.value)) != (nz := len(self.zones.value)):
                raise ValueError(f"Number od values in {self} ({nv}) does not match the number of zones ({nz})")


class ComputationSet(EFLRSet):
    """Model Computation EFLR."""

    set_type = 'COMPUTATION'
    logical_record_type = EFLRType.STATIC
    item_type = ComputationItem


ComputationItem.parent_eflr_class = ComputationSet
