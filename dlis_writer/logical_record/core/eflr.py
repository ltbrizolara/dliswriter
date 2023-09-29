from dlis_writer.utils.common import write_struct
from dlis_writer.utils.rp66 import RP66
from dlis_writer.utils.enums import RepresentationCode, LogicalRecordType
from dlis_writer.logical_record.core.attribute import Attribute
from dlis_writer.logical_record.core.iflr_eflr_base import IflrAndEflrBase


class EFLR(IflrAndEflrBase):
    """Represents an Explicitly Formatted Logical Record

    Attributes:
        object_name: Identifier of a Logical Record Segment. Must be
            distinct in a single Logical File.
        set_name: Optional identifier of the set a Logical Record Segment belongs to.

    """

    is_eflr = True
    logical_record_type: LogicalRecordType = NotImplemented

    def __init__(self, object_name: str, set_name: str = None, *args, **kwargs):
        super().__init__()

        self.object_name = object_name
        self.set_name = set_name

        self.origin_reference = None
        self.copy_number = 0

        self.is_dictionary_controlled = False
        self.dictionary_controlled_objects = None

        self._rp66_rules = getattr(RP66, self.set_type.replace('-', '_'))
        self._attributes: dict[str, Attribute] = {}

    def _create_attribute(self, key):
        rules = self._rp66_rules[key]

        attr = Attribute(
            label=key.strip('_').upper().replace('_', '-'),
            count=rules['count'],
            representation_code=rules['representation_code']
        )

        self._attributes[key] = attr

        return attr

    @property
    def obname(self) -> bytes:
        """Creates OBNAME bytes according to RP66 V1 spec

        Returns:
            OBNAME bytes that is used to identify an object in RP66 V1

        .._RP66 V1 OBNAME Representation Code:
            http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_23
        """

        return write_struct(
            RepresentationCode.OBNAME,
            (self.origin_reference, self.copy_number, self.object_name)
        )

    def make_set_component(self) -> bytes:
        """Creates component role Set

        Returns:
            Bytes that represent a Set component

        .._RP66 Component Descriptor:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_1
        """

        _bytes = write_struct(RepresentationCode.IDENT, self.set_type)
        if self.set_name:
            _bytes = b'\xf8' + _bytes + write_struct(RepresentationCode.IDENT, self.set_name)
        else:
            _bytes = b'\xf0' + _bytes

        return _bytes

    def make_template(self) -> bytes:
        """Creates template from EFLR object's attributes

        Returns:
            Template bytes compliant with the RP66 V1

        .._RP66 V1 Component Usage:
            http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_2_2

        """

        _bytes = b''
        for attr in self._attributes.values():
            _bytes += attr.get_as_bytes(for_template=True)

        return _bytes

    def make_object_component(self) -> bytes:
        """Creates object component"""

        return b'p' + self.obname

    def make_objects(self) -> bytes:
        """Creates object bytes that follows the object component

        Note:
            Each attribute of EFLR object is a logical_record.utils.core.Attribute instance
            Using Attribute instances' get_as_bytes method to create bytes.

        """

        _bytes = b''
        if self.is_dictionary_controlled:
            for obj in self.dictionary_controlled_objects:
                _bytes += obj.represent_as_bytes()
        else:
            for attr in self._attributes.values():
                if not attr.value:
                    _bytes += b'\x00'
                else:
                    _bytes += attr.get_as_bytes()

        return _bytes

    def make_body_bytes(self) -> bytes:
        """Writes Logical Record Segment bytes without header"""

        a = self.make_set_component()
        b = self.make_template()
        c = self.make_objects()

        if self.is_dictionary_controlled:
            return a + b + c

        d = self.make_object_component()
        return a + b + d + c

    def _write_struct_for_lr_type(self):
        return write_struct(RepresentationCode.USHORT, self.logical_record_type.value)
