from common.data_types import struct_type_dict
from common.data_types import write_struct

from utils.converters import get_ascii_bytes
from utils.converters import get_representation_code

from component import Set


class LogicalRecordSegment(object):

    def __init__(self,
                 segment_length:int=None, # Will be calculated after the segment is created
                 logical_record_type:int=None,
                 is_eflr:bool=True,
                 has_predecessor_segment:bool=False,
                 has_successor_segment:bool=False,
                 is_encrypted:bool=False,
                 has_encryption_protocol:bool=False,
                 has_checksum:bool=False,
                 has_trailing_length:bool=False,
                 has_padding:bool=False,
                 set_component:object=None):


        '''  


        :segment_length --> Integer. Denotes the length of logical record segment in bytes.
        
        :logical_record_type --> Integer denoting the Logical Record Type (to be converted to USHORT). 
        For all record types please see: http://w3.energistics.org/rp66/v1/rp66v1_appa.html#A_2
        For example, logical_record_type=0 will be type FHLR, which is "File Header"
        

        ATTRIBUTES
        
        All 8 arguments listed below must be provided with a value of either True or False.

        :is_eflr --> Abbreviation for "Explicitly Formatted Logical Record"
        :has_predecessor_segment
        :has_successor_segment
        :is_encrypted
        :has_encryption_protocol
        :has_checksum
        :has_trailing_length
        :has_padding
        
        To write these attributes, all 8 bits will be merged. Let's say is_eflr="1" and remaining 7 attributes="0".
        These attributes will be merged into a string "10000000" then we will get the int('10000000',2) and convert it to USHORT
        and append to DLIS file.

        RP66 V1 Section 3.2.3.2 Comment Number 2 (Under sub-header "Comments") explains this part:

            QUOTE
            2. The Logical Record Segment Attribute bits for Segment 
                    #1 indicate an EFLR structure (bit 1),
                    no predecessor segment (bit 2),
                    a successor segment (bit 3),
                    no encryption (bit 4),
                    no Encryption Packet (bit 5),
                    a checksum (bit 6),
                    a Trailing Length (bit 7),
                    and no Padding (bit 8)
            END QUOTE FROM --> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_3_2

        This table also displays Logical Record Segment Attributes --> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1


        First 2 bytes specify the "Logical Record Segment Length" and data type is UNORM
        Next 1 byte is an integer (type USHORT) and 



        :set_component -> Every logical record segment must have a set component.


        References:
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_2_2_1
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_1
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec3.html#3_2_3_2
            -> https://github.com/Teradata/dlispy/blob/b2d682dbfd8a6f7d0074351b603e22f97524fee6/dlispy/LogicalRecordSegment.py
        
        '''


        self.segment_length = segment_length
        self.logical_record_type = logical_record_type

        # Attributes
        self.is_eflr = str(int(is_eflr))
        self.has_predecessor_segment = str(int(has_predecessor_segment))
        self.has_successor_segment = str(int(has_successor_segment))
        self.is_encrypted = str(int(is_encrypted))
        self.has_encryption_protocol = str(int(has_encryption_protocol))
        self.has_checksum = str(int(has_checksum))
        self.has_trailing_length = str(int(has_trailing_length))
        self.has_padding = str(int(has_padding))

        # Set component
        self.set_component = set_component

        # Template
        self.template = None

        # Objects
        self.objects = []



    def get_as_bytes(self):



        # Constructing the body bytes first as we need to provide the lenght of the segment in the header.

        _body_bytes = b''

        # BODY
        if self.set_component:
            _body_bytes += self.set_component.get_as_bytes()

        if self.template:
            _body_bytes += self.template.get_as_bytes()

        for _object in self.objects:
            _body_bytes += _object.get_as_bytes()


        # HEADER

        if len(_body_bytes) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body_bytes) + 5)
        else:
            _length = write_struct('UNORM', len(_body_bytes) + 4)

        _logical_record_type = write_struct('USHORT', self.logical_record_type)
        _attributes = write_struct('USHORT',
            int(
                str(int(self.is_eflr))\
               +str(int(self.has_predecessor_segment))\
               +str(int(self.has_successor_segment))\
               +str(int(self.is_encrypted))\
               +str(int(self.has_encryption_protocol))\
               +str(int(self.has_checksum))\
               +str(int(self.has_trailing_length))\
               +str(int(self.has_padding)),
               2
            )
        )

        _header_bytes = _length + _attributes + _logical_record_type


        _bytes = _header_bytes + _body_bytes
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes


class IFLR(object):

    def __init__(self):
        pass


class EFLR(object):

    def __init__(self,
                 set_name:str=None,
                 origin_reference:int=None,
                 copy_number:int=0,
                 object_name:str=None,
                 has_padding:bool=False):

        self.set_name = set_name
        self.origin_reference = origin_reference
        self.copy_number = copy_number
        self.object_name = object_name
        self.has_padding = has_padding


    def finalize_bytes(self, logical_record_type, _body):
        # HEADER
        if len(_body) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body) + 5)
        else:
            _length = write_struct('UNORM', len(_body) + 4)

        _logical_record_type = write_struct('USHORT', logical_record_type)
        _attributes = write_struct('USHORT', int('1000000' + str(int(self.has_padding)), 2))

        _header = _length + _attributes + _logical_record_type


        _bytes = _header + _body
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes


class FileHeader(object):

    def __init__(self,
                 sequence_number:int=1,
                 _id:str='0'):

        self.sequence_number = sequence_number
        self._id = _id
        
        self.origin_reference = None
        self.copy_number = 0
        self.object_name = None


    def get_as_bytes(self):
        # HEADER
        _length = write_struct('UNORM', 124)
        _attributes = write_struct('USHORT', int('10000000', 2))
        _type = write_struct('USHORT', 0)

        _header_bytes = _length + _attributes + _type

        # BODY
        _body_bytes = b''
        _body_bytes += Set(set_type='FILE-HEADER').get_as_bytes()
        
        # TEMPLATE
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('ASCII', 'SEQUENCE-NUMBER')
        _body_bytes += write_struct('USHORT', 20)
        
        _body_bytes += write_struct('USHORT', int('00110100', 2))
        _body_bytes += write_struct('ASCII', 'ID')
        _body_bytes += write_struct('USHORT', 20)

        # OBJECT
        _body_bytes += write_struct('USHORT', int('01110000', 2))
        _body_bytes += write_struct('OBNAME', (self.origin_reference,
                                               self.copy_number,
                                               self.object_name))

        # ATTRIBUTES
        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 10)
        _body_bytes += get_ascii_bytes(self.sequence_number, 10, justify='right')
        _body_bytes += write_struct('USHORT', int('00100001', 2))
        _body_bytes += write_struct('USHORT', 65)
        _body_bytes += get_ascii_bytes(self._id, 65, justify='left')


        _bytes = _header_bytes + _body_bytes
        
        return _bytes


class Origin(EFLR):
    def __init__(self,
                 file_id:str=None,
                 file_set_name:str=None,
                 file_set_number:int=None,
                 file_number:int=None,
                 file_type:str=None,
                 product:str=None,
                 version:str=None,
                 programs:str=None,
                 creation_time=None,
                 order_number:str=None,
                 descent_number:int=None,
                 run_number:int=None,
                 well_id:int=None,
                 well_name:str=None,
                 field_name:str=None,
                 producer_code:int=None,
                 producer_name:str=None,
                 company:str=None,
                 name_space_name:str=None,
                 name_space_version:int=None):

        super().__init__()

        self.file_id = file_id
        self.file_set_name = file_set_name
        self.file_set_number = file_set_number
        self.file_number = file_number
        self.file_type = file_type
        self.product = product
        self.version = version
        self.programs = programs
        self.creation_time = creation_time
        self.order_number = order_number
        self.descent_number = descent_number
        self.run_number = run_number
        self.well_id = well_id
        self.well_name = well_name
        self.field_name = field_name
        self.producer_code = producer_code
        self.producer_name = producer_name
        self.company = company
        self.name_space_name = name_space_name
        self.name_space_version = name_space_version


    def get_as_bytes(self):
        _body = b''

        # Set
        _body += Set(set_type='ORIGIN', set_name=self.set_name).get_as_bytes()

        # Template
        if self.file_id:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-ID')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.file_set_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-SET-NAME')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.file_set_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-SET-NUMBER')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.file_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-NUMBER')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.file_type:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FILE-TYPE')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.product:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCT')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.version:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'VERSION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.programs:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PROGRAMS')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.creation_time:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CREATION-TIME')
            _body += write_struct('USHORT', get_representation_code('DTIME'))
        
        if self.order_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ORDER-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.descent_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCENT-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.run_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'RUN-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.well_id:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'WELL-ID')
            _body += write_struct('USHORT', get_representation_code('UVARI'))
        
        if self.well_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'WELL-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.field_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'FIELD-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.producer_code:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCER-CODE')
            _body += write_struct('USHORT', get_representation_code('UNORM'))
        
        if self.producer_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRODUCER-NAME')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.company:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'COMPANY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.name_space_name:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'NAME-SPACE-NAME')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.name_space_version:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'NAME-SPACE-VERSION')
            _body += write_struct('USHORT', get_representation_code('UVARI'))


        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES
        
        if self.file_id:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.file_id)
        
        if self.file_set_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.file_set_name)
        
        if self.file_set_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.file_set_number)
        
        if self.file_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.file_number)
        
        if self.file_type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.file_type)
        
        if self.product:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.product)
        
        if self.version:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.version)
        
        if self.programs:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.programs)
        
        if self.creation_time:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('DTIME', self.creation_time)
        
        if self.order_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.order_number)
        
        if self.descent_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.descent_number)
        
        if self.run_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.run_number)
        
        if self.well_id:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.well_id)
        
        if self.well_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.well_name)
        
        if self.field_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.field_name)
        
        if self.producer_code:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UNORM', self.producer_code)
        
        if self.producer_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.producer_name)
        
        if self.company:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.company)
        
        if self.name_space_name:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.name_space_name)
        
        if self.name_space_version:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('UVARI', self.name_space_version)


        # HEADER
        return self.finalize_bytes(1, _body)


class WellReferencePoint(EFLR):

    def __init__(self,
                 permanent_datum:str=None,
                 vertical_zero:str=None,
                 permanent_datum_elevation:float=None,
                 above_permanent_datum:float=None,
                 magnetic_declination:float=None,
                 coordinate_1_name:str=None,
                 coordinate_1_value:float=None,
                 coordinate_2_name:str=None,
                 coordinate_2_value:float=None,
                 coordinate_3_name:str=None,
                 coordinate_3_value:float=None):

        super().__init__()

        self.permanent_datum = permanent_datum
        self.vertical_zero = vertical_zero
        self.permanent_datum_elevation = permanent_datum_elevation
        self.above_permanent_datum = above_permanent_datum
        self.magnetic_declination = magnetic_declination
        self.coordinate_1_name = coordinate_1_name
        self.coordinate_1_value = coordinate_1_value
        self.coordinate_2_name = coordinate_2_name
        self.coordinate_2_value = coordinate_2_value
        self.coordinate_3_name = coordinate_3_name
        self.coordinate_3_value = coordinate_3_value



    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='WELL-REFERENCE', set_name=self.set_name).get_as_bytes()


        # TEMPLATE
        if self.permanent_datum:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PERMANENT-DATUM')
        if self.vertical_zero:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VERTICAL-ZERO')
        if self.permanent_datum_elevation:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PERMANENT-DATUM-ELEVATION')
        if self.above_permanent_datum:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'ABOVE-PERMANENT-DATUM')
        if self.magnetic_declination:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MAGNETIC-DECLINATION')
        if self.coordinate_1_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-1-NAME')
        if self.coordinate_1_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-1-VALUE')
        if self.coordinate_2_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-2-NAME')
        if self.coordinate_2_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-2-VALUE')
        if self.coordinate_3_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-3-NAME')
        if self.coordinate_3_value:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATE-3-VALUE')


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES

        if self.permanent_datum:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.permanent_datum)

        if self.vertical_zero:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.vertical_zero)

        if self.permanent_datum_elevation:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.permanent_datum_elevation)

        if self.above_permanent_datum:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 2)
            _body += write_struct('FDOUBL', self.above_permanent_datum)

        if self.magnetic_declination:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.magnetic_declination)

        if self.coordinate_1_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_1_name)

        if self.coordinate_1_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_1_value)

        if self.coordinate_2_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_2_name)

        if self.coordinate_2_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_2_value)

        if self.coordinate_3_name:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('ASCII', self.coordinate_3_name)

        if self.coordinate_3_value:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 7)
            _body += write_struct('FDOUBL', self.coordinate_3_value)


        return self.finalize_bytes(1, _body)


class Axis(EFLR):

    def __init__(self,
                 axis_id:str=None,
                 coordinates:list=None,
                 coordinates_struct_type:str='FDOUBL',
                 spacing:int=None):
        '''
        
        
        :axis_id -> Identifier
        
        :coordinates -> A list of coordinates (please see the quote below)
        
        :coordinates_struct_type -> Default data type is float, but
        if you pass string, this attribute must be set to 'ASCII' or 'IDENT'.
        (see below quote)

        :spacing -> signed spacing along the axis between successive coordinates,
        beginning at the last coordinate value specified by the coordinates attribute.


        QUOTE
            The Coordinates Attribute specifies explicit coordinate values 
            along a coordinate axis. 
            These values may be numeric (i.e., for non-uniform coordinate spacing),
            or they may be textual identifiers, for example "Near" and "Far".
            If the Coordinates Value has numeric Elements, 
            then they must occur in order of increasing or decreasing value.
            The Count of the Coordinates Attribute need not agree 
            with the number of array elements along this axis 
            specified by a related Dimension Attribute.
        END QUOTE FROM ->  RP66 V1 Section 5.3.1 -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_3_1

        
        References:
            -> http://w3.energistics.org/rp66/v1/rp66v1_sec5.html#5_3_1

        '''

        super().__init__()

        self.axis_id = axis_id
        if coordinates:
            self.coordinates = coordinates
        else:
            self.coordinates = []
        self.coordinates_struct_type = coordinates_struct_type
        self.spacing = spacing


    def get_as_bytes(self):
        _body = b''

        # SET
        _body += Set(set_type='AXIS', set_name=self.set_name).get_as_bytes()

        # TEMPLATE        
        if self.axis_id:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'AXIS-ID')
        
        if self.coordinates:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'COORDINATES')
        
        if self.spacing:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'SPACING')


        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES (VALUES)
        if self.axis_id:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('IDENT'))
            _body += write_struct('IDENT', self.axis_id)

        if self.coordinates:

            if len(self.coordinates) > 1:
                _body += write_struct('USHORT', int('00101101', 2))
                _body += write_struct('UVARI', len(self.coordinates))

                for coord in self.coordinates:
                    _body += write_struct(self.coordinates_struct_type, coord)

            else:
                _body += write_struct('USHORT', int('00100101', 2))
                _body += write_struct('USHORT', get_representation_code(self.coordinates_struct_type))
                _body += write_struct(get_representation_code(self.coordinates_struct_type), self.coordinates[0])

        if self.spacing:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', get_representation_code('SLONG'))
            _body += write_struct('SLONG', self.spacing)


        return self.finalize_bytes(2, _body)


    def get_obname_only(self):
        '''
        Axis object might be referenced from other Objects like Channels.
        The reference identifier is a 'OBNAME' attribute.
        This method returns only OBNAME attribute of this Axis object.

        '''

        return write_struct('OBNAME', (self.origin_reference,
                                       self.copy_number,
                                       self.object_name))


class LongName(EFLR):

    def __init__(self,
                 general_modifier:str=None,
                 quantity:str=None,
                 quantity_modifier:str=None,
                 altered_form:str=None,
                 entity:str=None,
                 entity_modifier:str=None,
                 entity_number:str=None,
                 entity_part:str=None,
                 entity_part_number:str=None,
                 generic_source:str=None,
                 source_part:str=None,
                 source_part_number:str=None,
                 conditions:str=None,
                 standard_symbol:str=None,
                 private_symbol:str=None):


        super().__init__()

        self.general_modifier = general_modifier
        self.quantity = quantity
        self.quantity_modifier = quantity_modifier
        self.altered_form = altered_form
        self.entity = entity
        self.entity_modifier = entity_modifier
        self.entity_number = entity_number
        self.entity_part = entity_part
        self.entity_part_number = entity_part_number
        self.generic_source = generic_source
        self.source_part = source_part
        self.source_part_number = source_part_number
        self.conditions = conditions
        self.standard_symbol = standard_symbol
        self.private_symbol = private_symbol


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='LONG-NAME', set_name=self.set_name).get_as_bytes()


        if self.general_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'GENERAL-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.quantity:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'QUANTITY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.quantity_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'QUANTITY-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.altered_form:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ALTERED-FORM')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_modifier:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-MODIFIER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_part:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-PART')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.entity_part_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENTITY-PART-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.generic_source:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'GENERIC-SOURCE')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.source_part:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SOURCE-PART')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.source_part_number:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SOURCE-PART-NUMBER')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.conditions:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CONDITIONS')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.standard_symbol:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'STANDARD-SYMBOL')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        if self.private_symbol:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'PRIVATE-SYMBOL')
            _body += write_struct('USHORT', get_representation_code('ASCII'))


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # ATTRIBUTES
        if self.general_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.general_modifier)
            
        if self.quantity:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.quantity)
            
        if self.quantity_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.quantity_modifier)
            
        if self.altered_form:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.altered_form)
            
        if self.entity:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity)
            
        if self.entity_modifier:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_modifier)
            
        if self.entity_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_number)
            
        if self.entity_part:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_part)
            
        if self.entity_part_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.entity_part_number)
            
        if self.generic_source:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.generic_source)
            
        if self.source_part:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.source_part)
            
        if self.source_part_number:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.source_part_number)
            
        if self.conditions:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.conditions)
            
        if self.standard_symbol:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.standard_symbol)
            
        if self.private_symbol:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.private_symbol)
            


        return self.finalize_bytes(9, _body)


# !!!!! COMPLETE Source Attribute (OBJREF)
class Channel(EFLR):
    def __init__(self,
                 long_name:str=None,
                 properties:list=None,
                 representation_code:str=None,
                 units:str=None,
                 dimension:list=None,
                 axis=None,
                 element_limit:list=None,
                 source=None):

        super().__init__()

        self.long_name = long_name
        self.properties = properties
        self.representation_code = representation_code
        self.units = units
        self.dimension = dimension
        self.axis = axis
        self.element_limit = element_limit
        self.source = source

    def get_as_bytes(self):
        _bytes = b''
        _bytes += write_struct('USHORT', int('01110000', 2))
        _bytes += write_struct('OBNAME', (self.origin_reference,
                                          self.copy_number,
                                          self.object_name))

        if self.long_name:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('ASCII', self.long_name)
        else:
            _bytes += self.write_absent_attribute()

        
        if self.properties:
            if len(self.properties) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.properties))

                for prop in self.properties:
                    _bytes += write_struct('IDENT', prop)

            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('IDENT', self.dimension[0])
        else:
            _bytes += self.write_absent_attribute()


        
        if self.representation_code:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('USHORT', get_representation_code(self.representation_code))

        else:
            _bytes += self.write_absent_attribute()
        

        if self.units:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += write_struct('UNITS', self.units)

        else:
            _bytes += self.write_absent_attribute()
        

        if self.dimension:
            if len(self.dimension) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.dimension))
                for dim in self.dimension:
                    _bytes += write_struct('UVARI', dim)

            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('UVARI', self.dimension[0])
            
        else:
            _bytes += self.write_absent_attribute()
        

        if self.axis:
            _bytes += write_struct('USHORT', int('00100001', 2))
            _bytes += self.axis.get_obname_only()

        else:
            _bytes += self.write_absent_attribute()
        

        if self.element_limit:
            if len(self.element_limit) > 1:
                _bytes += write_struct('USHORT', int('00101001', 2))
                _bytes += write_struct('UVARI', len(self.element_limit))
                for el in self.element_limit:
                    _bytes += write_struct('UVARI', el)
            else:
                _bytes += write_struct('USHORT', int('00100001', 2))
                _bytes += write_struct('UVARI', self.element_limit[0])
            
        else:
            _bytes += self.write_absent_attribute()
        

        # NEEDS REFACTORING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if self.source:
            pass
        else:
            _bytes += self.write_absent_attribute()

        return _bytes

    def write_absent_attribute(self):
        return write_struct('USHORT', int('00000000', 2))

    def get_obname_only(self):
        '''
        
        Channel Objects are referenced in Frame Objects using OBNAME attribute.

        '''

        return write_struct('OBNAME', (self.origin_reference,
                                       self.copy_number,
                                       self.object_name))


class ChannelLogicalRecord(EFLR):
    def __init__(self,
                 channels:list=None):

        super().__init__()

        if channels:
            self.channels = channels
        else:
            self.channels = []
    
    def get_as_bytes(self):
        _body = b''

        # SET
        _body += Set(set_type='CHANNEL', set_name=self.set_name).get_as_bytes()

        # TEMPLATE

        
        # if self.long_name:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'LONG-NAME')
        _body += write_struct('USHORT', get_representation_code('ASCII'))
    
        # if self.properties:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'PROPERTIES')
        _body += write_struct('USHORT', get_representation_code('IDENT'))
    
        # if self.representation_code:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'REPRESENTATION-CODE')
        _body += write_struct('USHORT', get_representation_code('USHORT'))
    
        # if self.units:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'UNITS')
        _body += write_struct('USHORT', get_representation_code('UNITS'))
    
        # if self.dimension:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'DIMENSION')
        _body += write_struct('USHORT', get_representation_code('UVARI'))
    
        # if self.axis:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'AXIS')
        _body += write_struct('USHORT', get_representation_code('OBNAME'))
    
        # if self.element_limit:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'ELEMENT-LIMIT')
        _body += write_struct('USHORT', get_representation_code('UVARI'))
    
        # if self.source:
        _body += write_struct('USHORT', int('00110100', 2))
        _body += write_struct('IDENT', 'SOURCE')
        _body += write_struct('USHORT', get_representation_code('OBJREF'))


        # add each Channel object here

        for channel_object in self.channels:
            _body += channel_object.get_as_bytes()


        return self.finalize_bytes(3, _body)


class Frame(EFLR):

    def __init__(self,
                 description:str=None,
                 channels:list=None,
                 index_type:str=None,
                 direction:str=None,
                 spacing:float=None,
                 spacing_units:str=None,
                 encrypted:bool=False,
                 index_min:int=None,
                 index_max:int=None):

        super().__init__()

        self.description = description
        if channels:
            self.channels = channels
        else:
            self.channels = []
        self.index_type = index_type
        self.direction = direction
        self.spacing = spacing
        self.spacing_units = spacing_units
        self.encrypted = encrypted
        self.index_min = index_min
        self.index_max = index_max


    def get_as_bytes(self):

        _body = b''

        # SET
        _body += Set(set_type='FRAME').get_as_bytes()

        # TEMPLATE
        if self.description:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DESCRIPTION')
            _body += write_struct('USHORT', get_representation_code('ASCII'))
        
        if self.channels:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'CHANNELS')
            _body += write_struct('USHORT', get_representation_code('OBNAME'))
        
        if self.index_type:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-TYPE')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.direction:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'DIRECTION')
            _body += write_struct('USHORT', get_representation_code('IDENT'))
        
        if self.spacing:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'SPACING')
            _body += write_struct('USHORT', get_representation_code('FDOUBL'))
        
        if self.encrypted:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'ENCRYPTED')
            _body += write_struct('USHORT', get_representation_code('USHORT'))
        
        if self.index_min:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-MIN')
            _body += write_struct('USHORT', get_representation_code('SLONG'))
        
        if self.index_max:
            _body += write_struct('USHORT', int('00110100', 2))
            _body += write_struct('IDENT', 'INDEX-MAX')
            _body += write_struct('USHORT', get_representation_code('SLONG'))

        # OBJECT
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))

        # ATTRIBUTES
        if self.description:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('ASCII', self.description)

        if self.channels:
            if len(self.channels) > 1:
                _body += write_struct('USHORT', int('00101001', 2))
                _body += write_struct('UVARI', len(self.channels))

                for channel in self.channels:
                    _body += channel.get_obname_only()
            else:
                _body += write_struct('USHORT', int('00100001', 2))
                _body += self.channels[0].get_obname_only()

        if self.index_type:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.index_type)

        if self.direction:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('IDENT', self.direction)

        if self.spacing:
            if self.spacing_units:
                _body += write_struct('USHORT', int('00100011', 2))
                _body += write_struct('UNITS', self.spacing_units)
                _body += write_struct('FDOUBL', self.spacing)
            else:
                _body += write_struct('USHORT', int('00100001', 2))
                _body += write_struct('FDOUBL', self.spacing)

        if self.encrypted:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('USHORT', int(self.encrypted))

        if self.index_min:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('SLONG', self.index_min)

        if self.index_max:
            _body += write_struct('USHORT', int('00100001', 2))
            _body += write_struct('SLONG', self.index_max)


        return self.finalize_bytes(4, _body)


    def get_obname_only(self):
        '''
    
        Frame Object is referenced from FrameData using OBNAME

        '''
        return write_struct('OBNAME', (self.origin_reference,
                                       self.copy_number,
                                       self.object_name))


class FrameData(IFLR):

    def __init__(self,
                 frame=None,
                 frame_number:int=None,
                 slots=None):

        '''
    
        FrameData is an Implicitly Formatted Logical Record (IFLR)

        Each FrameData object begins with a reference to the Frame object
        that they belong to using OBNAME.

        :frame -> A Frame(EFLR) object instance
        :position -> Auto-assigned integer denoting the position of the FrameData
        
        :slots -> Represents a row in the dataframe. If there are 3 channels, slots will be the array
        of values at the corresponding index for those channels.

        '''


        self.frame = frame
        self.frame_number = frame_number # UVARI
        self.slots = slots # np.ndarray


    def finalize_bytes(self, _body):
        
        
        _length = len(_body) + 4
        if _length % 2 == 0:
            _attributes = write_struct('USHORT', int('00000000', 2))
            _has_padding = False
        else:
            _attributes = write_struct('USHORT', int('00000001', 2))
            _length += 1
            _has_padding = True

        
        _header = b''
        _header += write_struct('UNORM', _length)
        _header += _attributes
        _header += write_struct('USHORT', 0) # Logical Record Type



        _bytes = _header + _body

        if _has_padding:
            _bytes += write_struct('USHORT', 0)

        return _bytes


    def get_as_bytes(self):

        _body = b''

        _body += self.frame.get_obname_only()
        _body += write_struct('UVARI', self.frame_number)
        
        for i in range(len(self.slots)):

            data = self.slots[i] # NP array
            # data = list(data.flatten('F'))

            # Get representation code from corresponding Channel
            representation_code = self.frame.channels[i].representation_code

            if type(data) == list:
                for value in data:
                    _body += write_struct(representation_code, value)

            else:
                _body += write_struct(representation_code, data)

        return self.finalize_bytes(_body)




class Equipment(object):

    def __init__(self,
                 set_name:str=None,
                 origin_reference:int=None,
                 copy_number:int=0,
                 object_name:str=None,
                 trademark_name:str=None,
                 status:bool=True,
                 _type:str=None,
                 serial_number:str=None,
                 location:str=None,
                 height:float=None,
                 height_units:float=None,
                 length:float=None,
                 length_units:float=None,
                 minimum_diameter:float=None,
                 minimum_diameter_units:float=None,
                 maximum_diameter:float=None,
                 maximum_diameter_units:float=None,
                 volume:float=None,
                 volume_units:float=None,
                 weight:float=None,
                 weight_units:float=None,
                 hole_size:float=None,
                 hole_size_units:float=None,
                 pressure:float=None,
                 pressure_units:float=None,
                 temperature:float=None,
                 temperature_units:float=None,
                 vertical_depth:float=None,
                 vertical_depth_units:float=None,
                 radial_drift:float=None,
                 radial_drift_units:float=None,
                 angular_drift:float=None,
                 angular_drift_units:float=None,
                 has_padding:bool=False):

        self.set_name = set_name
        self.origin_reference = origin_reference
        self.copy_number = copy_number
        self.object_name = object_name
        
        self.trademark_name = trademark_name
        self.status = status
        self._type = _type
        self.serial_number = serial_number
        self.location = location
        self.height = height
        self.height_units = height_units
        self.length = length
        self.length_units = length_units
        self.minimum_diameter = minimum_diameter
        self.minimum_diameter_units = minimum_diameter_units
        self.maximum_diameter = maximum_diameter
        self.maximum_diameter_units = maximum_diameter_units
        self.volume = volume
        self.volume_units = volume_units
        self.weight = weight
        self.weight_units = weight_units
        self.hole_size = hole_size
        self.hole_size_units = hole_size_units
        self.pressure = pressure
        self.pressure_units = pressure_units
        self.temperature = temperature
        self.temperature_units = temperature_units
        self.vertical_depth = vertical_depth
        self.vertical_depth_units = vertical_depth_units
        self.radial_drift = radial_drift
        self.radial_drift_units = radial_drift_units
        self.angular_drift = angular_drift
        self.angular_drift_units = angular_drift_units

        self.has_padding = has_padding



    def get_as_bytes(self):

        # Body
        _body = b''

        # Set
        _body += Set(set_type='EQUIPMENT', set_name=self.set_name).get_as_bytes()

        # Template
        if self.trademark_name:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TRADEMARK-NAME')

        if self.status:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'STATUS')

        if self._type:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TYPE')

        if self.serial_number:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'SERIAL-NUMBER')

        if self.location:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'LOCATION')


        if self.height:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'HEIGHT')
        
        if self.length:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'LENGTH')
        
        if self.minimum_diameter:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MINIMUM-DIAMETER')
        
        if self.maximum_diameter:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'MAXIMUM-DIAMETER')
        
        if self.volume:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VOLUME')
        
        if self.weight:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'WEIGHT')
       
        if self.hole_size:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'HOLE-SIZE')
        
        if self.pressure:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'PRESSURE')
        
        if self.temperature:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'TEMPERATURE')
        
        if self.vertical_depth:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'VERTICAL-DEPTH')
        
        if self.radial_drift:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'RADIAL-DRIFT')
        
        if self.angular_drift:
            _body += write_struct('USHORT', int('00110000', 2))
            _body += write_struct('IDENT', 'ANGULAR-DRIFT')


        # Object
        _body += write_struct('USHORT', int('01110000', 2))
        _body += write_struct('OBNAME', (self.origin_reference,
                                         self.copy_number,
                                         self.object_name))


        # Attributes (VALUES)
        
        if self.trademark_name:
            print('Creating TM ATTTTTRRR')
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 20)
            _body += write_struct('IDENT', self.trademark_name)

        if self.status:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 26)
            _body += write_struct('USHORT', int(self.status))

        if self._type:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self._type)

        if self.serial_number:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self.serial_number)

        if self.location:
            _body += write_struct('USHORT', int('00100101', 2))
            _body += write_struct('USHORT', 19)
            _body += write_struct('IDENT', self.location)

        if self.height:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.height_units:
                units = write_struct('IDENT', self.height_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.height)

        if self.length:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.length_units:
                units = write_struct('IDENT', self.length_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.length)

        if self.minimum_diameter:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.minimum_diameter_units:
                units = write_struct('IDENT', self.minimum_diameter_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.minimum_diameter)

        if self.maximum_diameter:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.maximum_diameter_units:
                units = write_struct('IDENT', self.maximum_diameter_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.maximum_diameter)

        if self.volume:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.volume_units:
                units = write_struct('IDENT', self.volume_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.volume)

        if self.weight:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.weight_units:
                units = write_struct('IDENT', self.weight_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.weight)

        if self.hole_size:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.hole_size_units:
                units = write_struct('IDENT', self.hole_size_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.hole_size)

        if self.pressure:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.pressure_units:
                units = write_struct('IDENT', self.pressure_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.pressure)

        if self.temperature:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.temperature_units:
                units = write_struct('IDENT', self.temperature_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.temperature)

        if self.vertical_depth:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.vertical_depth_units:
                units = write_struct('IDENT', self.vertical_depth_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.vertical_depth)

        if self.radial_drift:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.radial_drift_units:
                units = write_struct('IDENT', self.radial_drift_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.radial_drift)

        if self.angular_drift:
            descriptive_bits = '001001'
            representation_code = write_struct('USHORT', 2)
            units = None
            if self.angular_drift_units:
                units = write_struct('IDENT', self.angular_drift_units)
                descriptive_bits += '11'
            else:
                descriptive_bits += '01'

            _body += write_struct('USHORT', int(descriptive_bits, 2))
            _body += write_struct('USHORT', 2)

            if units:
                _body += units
            _body += write_struct('FSINGL', self.angular_drift)



        # HEADER
        if len(_body) % 2 != 0:
            self.has_padding = True
            _length = write_struct('UNORM', len(_body) + 5)
        else:
            _length = write_struct('UNORM', len(_body) + 4)

        _logical_record_type = write_struct('USHORT', 5)
        _attributes = write_struct('USHORT', int('1000000' + str(int(self.has_padding)), 2))

        _header = _length + _attributes + _logical_record_type


        _bytes = _header + _body
        if self.has_padding:
            _bytes += write_struct('USHORT', 1)

        return _bytes






class EOD(object):
    def get_as_bytes(self, frame):
        


        _body = b''
        _body += frame.get_obname_only()
        _body += write_struct('USHORT', 0)

        _length = len(_body + 4)
        if _length % 2 == 0:
            _attributes = write_struct('USHORT', int('00000000', 2))
            _has_padding = False
        else:
            _attributes = write_struct('USHORT', int('00000001', 2))
            _length += 1
            _has_padding = True

        # HEADER

        _header = b''
        _header += write_struct('UNORM', _length)
        _header += _attributes
        _header += write_struct('USHORT', 127)

        _bytes = _header + _body

        if has_padding:
            _bytes += write_struct('USHORT', 0)


        return _bytes


