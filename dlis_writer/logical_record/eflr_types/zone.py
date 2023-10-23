from numbers import Number
from datetime import datetime, timedelta

from dlis_writer.logical_record.core import EFLR
from dlis_writer.utils.enums import LogicalRecordType, RepresentationCode as RepC
from dlis_writer.logical_record.core.attribute import Attribute


class Zone(EFLR):
    set_type = 'ZONE'
    logical_record_type = LogicalRecordType.STATIC
    domains = ('BOREHOLE-DEPTH', 'TIME', 'VERTICAL-DEPTH')

    def __init__(self, name: str, set_name: str = None, **kwargs):
        """

        :description -> str

        :domain -> 3 options:
            BOREHOLE-DEPTH
            TIME
            VERTICAL-DEPTH

        :maximum -> Depending on the 'domain' attribute, this is either
        max-depth (dtype: float) or the latest time (dtype: datetime.datetime)

        :minimum -> Depending on the 'domain' attribute, this is either
        min-depth (dtype: float) or the earliest time (dtype: datetime.datetime)

        """

        super().__init__(name, set_name)

        self.description = Attribute('description', representation_code=RepC.ASCII)
        self.domain = Attribute('domain', converter=self.check_domain, representation_code=RepC.IDENT)
        self.maximum = Attribute('maximum', converter=self.parse_number_or_dtime)
        self.minimum = Attribute('minimum', converter=self.parse_number_or_dtime)

        self.set_attributes(**kwargs)

    @classmethod
    def check_domain(cls, domain):
        if domain not in cls.domains:
            raise ValueError(f"'domain' should be one of: {', '.join(cls.domains)}; got {domain}")
        return domain

    @classmethod
    def parse_number_or_dtime(cls, value):
        if value is None:
            return value

        if isinstance(value, (Number, datetime, timedelta)):
            return value

        if not isinstance(value, str):
            raise TypeError(f"Expected a number, datetime, timedelta, or a string; got {type(value)}: {value}")

        for parser in (cls.parse_dtime, int, float):
            try:
                return parser(value)
            except ValueError:
                pass

        raise ValueError(f"Couldn't parse value: '{value}'")

