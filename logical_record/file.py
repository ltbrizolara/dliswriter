import numpy as np
import logging
from functools import lru_cache
from line_profiler_pycharm import profile
from progressbar import progressbar  # package name is progressbar2 (added to requirements)

from logical_record.utils.common import write_struct
from logical_record.utils.enums import RepresentationCode


FORMAT = '[%(levelname)s] %(asctime)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)


class DLISFile(object):
    """Top level object that creates DLIS file from given list of logical record segment bodies

    Attributes:
        file_path: Absolute or relative path of output DLIS file
        storage_unit_label: A logical_record.storage_unit_label.StorageUnitLabel instance
        file_header: A logical_record.file_header.FileHeader instance
        origin: A logical_record.origin.Origin instance
        logical_records: List containing ALL logical record segments in the DLIS file
        visible_records: List of visible records that are created on the fly
        visible_record_length: Maximum length of each visible record

    .._RP66 V1 Maximum Visible Record Length:
        http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
    """

    def __init__(self, storage_unit_label, file_header, origin, visible_record_length: int = None):
        """Initiates the object with given parameters"""
        self.pos = {}
        self.storage_unit_label = storage_unit_label
        self.file_header = file_header
        self.origin = origin
        self.visible_records = []

        self.visible_record_length = visible_record_length if visible_record_length else 8192
        self._vr_struct = write_struct(RepresentationCode.USHORT, 255) + write_struct(RepresentationCode.USHORT, 1)

    @lru_cache
    def visible_record_bytes(self, length: int) -> bytes:
        """Create Visible Record object as bytes
        
        Args:
            length: Length of the visible record

        Returns:
            Visible Record object bytes

        """

        return write_struct(RepresentationCode.UNORM, length) + self._vr_struct

    def validate(self):
        """Validates the object according to RP66 V1 rules"""
        logger.info('Validating... ')
        if not self.origin.file_set_number.value:
            raise Exception('Origin object MUST have a file_set_number')

        assert self.visible_record_length >= 20, 'Minimum visible record length is 20 bytes'
        assert self.visible_record_length <= 16384, 'Maximum visible record length is 16384 bytes'
        assert self.visible_record_length % 2 == 0, 'Visible record length must be an even number'

    def assign_origin_reference(self, logical_records):
        """Assigns origin_reference attribute to self.origin.file_set_number for all Logical Records"""
        logger.info('Assigning...')

        val = self.origin.file_set_number.value
        logger.debug(f"File set number is {val}")

        self.file_header.origin_reference = val
        self.origin.origin_reference = val
        for logical_record in logical_records:
            logical_record.origin_reference = val

            if hasattr(logical_record, 'is_dictionary_controlled') \
                    and logical_record.dictionary_controlled_objects is not None:
                for obj in logical_record.dictionary_controlled_objects:
                    obj.origin_reference = val

    @profile
    def raw_bytes(self, logical_records):
        """Writes bytes of entire file without Visible Record objects and splits"""
        logger.info('Writing raw bytes...')

        all_records = [self.storage_unit_label, self.file_header, self.origin] + logical_records

        n = len(all_records)
        all_records_bytes = [None] * n
        all_lengths = [None] * n
        all_positions = [0] + [None] * n
        current_pos = 0
        for i, lr in enumerate(all_records):
            b = lr.as_bytes # grows with data size more than row number
            all_records_bytes[i] = b
            all_lengths[i] = len(b)
            current_pos += all_lengths[i]
            all_positions[i+1] = current_pos
        # all_records_bytes = [lr.as_bytes for lr in all_records]

        all_lengths = [len(lr) for lr in all_records_bytes]
        all_positions = np.concatenate(([0], np.cumsum(all_lengths)))#[sum(all_lengths[:i]) for i in range(n+1)] # 92% time spent here for 1 line
        print(all_positions[-1])
        raw_bytes = bytearray(bytes(all_positions[-1]*2))

        for i in range(n):
            raw_bytes[all_positions[i]:all_positions[i+1]] = all_records_bytes[i]
            self.pos[all_records[i]] = all_positions[i]

        return raw_bytes

    @profile
    def create_visible_record_dictionary(self, logical_records):
        """Creates a dictionary that guides in which positions Visible Records must be added and which
        Logical Record Segments must be split

        Returns:
            A dict object containing Visible Record split positions and related information

        """

        all_lrs = [self.file_header, self.origin] + logical_records
        n_lrs = len(all_lrs)
        visible_record_length = self.visible_record_length

        q = {}

        _vr_length = 4
        _number_of_vr = 1
        _idx = 0
        vr_offset = 0
        number_of_splits = 0

        while True:

            vr_position = (visible_record_length * (_number_of_vr - 1)) + 80  # DON'T TOUCH THIS
            vr_position += vr_offset
            if _idx == n_lrs:
                q[vr_position] = {
                    'length': _vr_length,
                    'split': None,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }
                break

            lrs = all_lrs[_idx]
            lrs_size = lrs.size

            _lrs_position = self.get_lrs_position(lrs, _number_of_vr, number_of_splits)
            position_diff = vr_position + visible_record_length - _lrs_position  # idk how to call this, but it's reused

            # NO NEED TO SPLIT KEEP ON
            if (_vr_length + lrs_size) <= visible_record_length:
                _vr_length += lrs_size
                _idx += 1

            # NO NEED TO SPLIT JUST DON'T ADD THE LAST LR
            elif position_diff < 16:
                q[vr_position] = {
                    'length': _vr_length,
                    'split': None,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }

                _vr_length = 4
                _number_of_vr += 1
                vr_offset -= position_diff

            else:
                q[vr_position] = {
                    'length': visible_record_length,
                    'split': lrs,
                    'number_of_prior_splits': number_of_splits,
                    'number_of_prior_vr': _number_of_vr
                }

                _vr_length = 8 + lrs_size - position_diff
                _number_of_vr += 1
                _idx += 1
                number_of_splits += 1

        return q

    @profile
    def add_visible_records(self, logical_records, raw_bytes):
        """Adds visible record bytes and undertakes split operations with the guidance of vr_dict
        received from self.create_visible_record_dictionary()

        """

        splits = 0

        logger.info("Creating visible record dictionary...")
        vr_dict = self.create_visible_record_dictionary(logical_records)
        logger.info('visible record dictionary created')

        # added bytes: 4 bytes per visible record and 4 per header  # TODO: is it always 4?
        total_vr_length = 4 * len(vr_dict)
        total_header_length = 4 * sum(int(bool(val['split'])) for val in vr_dict.values())
        total_added_length = total_vr_length + total_header_length

        total_len = len(raw_bytes) + total_added_length
        empty_bytes = np.zeros(total_len, dtype=np.uint8)
        empty_header_bytes = np.zeros(total_len, dtype=np.uint8)
        mask = np.zeros(total_len, dtype=bool)
        header_mask = np.zeros(total_len, dtype=bool)

        logger.info('Adding visible records...')
        for vr_position, val in progressbar(vr_dict.items()):

            vr_length = val['length']
            lrs_to_split = val['split']
            number_of_prior_splits = val['number_of_prior_splits']
            number_of_prior_vr = val['number_of_prior_vr']

            self.insert_bytes(
                empty_bytes,
                bytes_to_insert=self.visible_record_bytes(vr_length),
                position=vr_position,
                mask=mask
            )

            if lrs_to_split:
                splits += 1
                # FIRST PART OF THE SPLIT
                updated_lrs_position = self.pos[lrs_to_split] \
                                       + (number_of_prior_splits * 4) \
                                       + (number_of_prior_vr * 4)

                first_segment_length = vr_position + vr_length - updated_lrs_position
                header_bytes_to_replace = lrs_to_split.split(
                    is_first=True,
                    is_last=False,
                    segment_length=first_segment_length,
                    add_extra_padding=False
                )

                self.insert_bytes(
                    empty_header_bytes,
                    bytes_to_insert=header_bytes_to_replace,
                    position=updated_lrs_position,
                    mask=header_mask
                )

                # SECOND PART OF THE SPLIT
                second_lrs_position = vr_position + vr_length + 4
                second_segment_length = lrs_to_split.size - first_segment_length + 4
                header_bytes_to_insert = lrs_to_split.split(
                    is_first=False,
                    is_last=True,
                    segment_length=second_segment_length,
                    add_extra_padding=False
                )

                self.insert_bytes(
                    empty_bytes,
                    bytes_to_insert=header_bytes_to_insert,
                    position=second_lrs_position - 4,
                    mask=mask
                )

        logger.info(f"{splits} splits created.")

        empty_bytes[~mask] = raw_bytes
        empty_bytes[header_mask] = empty_header_bytes[header_mask]

        raw_bytes_with_vr = empty_bytes.tobytes()
        return raw_bytes_with_vr

    @staticmethod
    def check_length(bytes_to_check, expected_length=4):
        if (nb := len(bytes_to_check)) != expected_length:
            raise ValueError(f"Expected {expected_length} bytes, got {nb}")

    @profile
    def insert_bytes(self, byte_array, bytes_to_insert, position, mask=None):
        self.check_length(bytes_to_insert)

        if mask is not None:
            if mask[position]:
                mask[position + 4:position + 8] = mask[position:position + 4]
                byte_array[position + 4:position + 8] = byte_array[position:position + 4]
            mask[position:position + 4] = True
        byte_array[position:position + 4] = np.frombuffer(bytes_to_insert, dtype=np.uint8)

    def get_lrs_position(self, lrs, number_of_vr: int, number_of_splits: int):
        """Recalculates the Logical Record Segment's position

        Args:
            lrs: A logical_record.utils.core.EFLR or logical_record.utils.core.IFLR instance
            number_of_vr: Number of visible records created prior to lrs' position
            number_of_splits: Number of splits occured prior to lrs' position

        Returns:
            Recalculated position of the Logical Record Segment in the entire file

        """
        return self.pos[lrs] + (number_of_vr * 4) + (number_of_splits * 4)

    @staticmethod
    def write_bytes_to_file(raw_bytes, filename):
        """Writes the bytes to a DLIS file"""
        logger.info('Writing to file...')

        with open(filename, 'wb') as f:
            f.write(raw_bytes)

        logger.info(f"Data written to file: '{filename}'")

    @profile
    def write_dlis(self, logical_records, filename):
        """Top level method that calls all the other methods to create and write DLIS bytes"""
        self.validate()
        self.assign_origin_reference(logical_records)
        raw_bytes = self.raw_bytes(logical_records)
        raw_bytes = self.add_visible_records(logical_records, raw_bytes)
        self.write_bytes_to_file(raw_bytes, filename)
        logger.info('Done.')
