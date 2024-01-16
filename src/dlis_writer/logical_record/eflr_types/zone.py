from typing import Any

from dlis_writer.logical_record.core.eflr import EFLRSet, EFLRItem
from dlis_writer.utils.enums import EFLRType
from dlis_writer.logical_record.core.attribute import IdentAttribute, DTimeAttribute, TextAttribute


class ZoneItem(EFLRItem):
    """Model an object being part of Zone EFLR."""

    parent: "ZoneSet"

    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')  #: allowed values for 'domain' Attribute

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialise ZoneItem.

        Args:
            name        :   Name of the ZoneItem.
            **kwargs    :   Values of to be set as characteristics of the ZoneItem Attributes.
        """

        self.description = TextAttribute('description', parent_eflr=self)
        self.domain = IdentAttribute('domain', converter=self.check_domain, parent_eflr=self)
        self.maximum = DTimeAttribute('maximum', allow_float=True, parent_eflr=self)
        self.minimum = DTimeAttribute('minimum', allow_float=True, parent_eflr=self)

        super().__init__(name, **kwargs)

    @classmethod
    def check_domain(cls, domain: str) -> str:
        """Check that the provided 'domain' value is allowed by the standard. Raise a ValueError otherwise."""

        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain


class ZoneSet(EFLRSet):
    """Model Zone EFLR."""

    set_type = 'ZONE'
    logical_record_type = EFLRType.STATIC
    item_type = ZoneItem


ZoneItem.parent_eflr_class = ZoneSet
