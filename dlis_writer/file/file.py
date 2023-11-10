import os
import logging
from line_profiler_pycharm import profile
from progressbar import ProgressBar  # package name is progressbar2 (added to requirements)
from typing import Union

from dlis_writer.utils.common import write_struct
from dlis_writer.utils.enums import RepresentationCode
from dlis_writer.logical_record.collections.logical_record_collection import LogicalRecordCollection
from dlis_writer.logical_record.collections.multi_frame_data import MultiFrameData
from dlis_writer.logical_record.core.logical_record_bytes import LogicalRecordBytes


logger = logging.getLogger(__name__)


def log_progress(message):
    """Wrap a function, so that log messages are displayed: a custom message at the start and 'Done' at the end."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(message)
            result = func(*args, **kwargs)
            logger.debug("Done")
            return result
        return wrapper
    return decorator


class DLISFile:
    """Top level object that creates DLIS file from given list of logical record segment bodies

    Attributes:
        storage_unit_label: A logical_record.storage_unit_label.StorageUnitLabel instance
        file_header: A logical_record.file_header.FileHeader instance
        origin: A logical_record.origin.Origin instance
        visible_record_length: Maximum length of each visible record

    .._RP66 V1 Maximum Visible Record Length:
        http://w3.energistics.org/rp66/v1/rp66v1_sec2.html#2_3_6_5
    """

    def __init__(self, visible_record_length: int = 8192):
        """Initiates the object with given parameters"""

        self.check_visible_record_length(visible_record_length)
        self.visible_record_length = visible_record_length

        # format version is a required part of each visible record and is fixed for a given version of the standard
        self._format_version = write_struct(RepresentationCode.USHORT, 255) + write_struct(RepresentationCode.USHORT, 1)

    @staticmethod
    def check_visible_record_length(vrl):
        if vrl < 20:
            raise ValueError("Visible record length must be at least 20 bytes")

        if vrl > 16384:
            raise ValueError("Visible record length cannot be larger than 16384 bytes")

        if vrl % 2:
            raise ValueError("Visible record length must be an even number")

    @staticmethod
    def assign_origin_reference(logical_records: LogicalRecordCollection):
        """Assigns origin_reference attribute to self.origin.file_set_number for all Logical Records"""

        val = logical_records.origin.first_object.file_set_number.value

        if not val:
            raise Exception('Origin object MUST have a file_set_number')

        logger.info(f"Assigning origin reference: {val} to all logical records")
        logical_records.set_origin_reference(val)

    @profile
    def make_bytes_of_logical_records(self, logical_records: LogicalRecordCollection):
        """Writes bytes of entire file without Visible Record objects and splits"""

        def wrapper():
            for lr in logical_records:
                if isinstance(lr, MultiFrameData):
                    for frame_data in lr:
                        yield frame_data.represent_as_bytes()
                else:
                    yield lr.represent_as_bytes()

        return wrapper()

    def _make_visible_record(self, body, size=None) -> bytes:

        if size is None:
            size = len(body)

        if size > self.visible_record_length - 4:
            raise ValueError(f"Body length is too large; got {size}, max is {self.visible_record_length - 4}")

        return write_struct(RepresentationCode.UNORM, size + 4) + self._format_version + body

    @log_progress("Creating visible records of the DLIS...")
    @profile
    def create_visible_records(self, n_records, all_lrb_iter) -> bytes:
        """Adds visible record bytes and undertakes split operations with the guidance of vr_dict
        received from self.create_visible_record_dictionary()

        """

        hs = 4  # header size (both for logical record segment and visible record)
        mbs = 12  # minimum logical record body size (min LRS size is 16 incl. 4-byte header)

        bar = ProgressBar(max_value=n_records)

        output = next(all_lrb_iter).bytes  # SUL - add as-is, don't wrap in a visible record

        current_vr_body = b''
        current_vr_body_size = 0
        max_vr_body_size = self.visible_record_length - hs
        position_in_current_lrb = 0

        lrb: LogicalRecordBytes = None
        i = 0
        remaining_vr_space = max_vr_body_size - hs
        remaining_lrb_size = 0

        def next_vr():
            nonlocal output, current_vr_body_size, current_vr_body, remaining_vr_space
            output += self._make_visible_record(current_vr_body, size=current_vr_body_size)
            current_vr_body = b''
            current_vr_body_size = 0
            remaining_vr_space = max_vr_body_size - 4

        def next_lrb():
            nonlocal lrb, i, position_in_current_lrb, remaining_lrb_size
            try:
                lrb = next(all_lrb_iter)
            except StopIteration:
                return False
            else:
                bar.update(i)
                i += 1
                position_in_current_lrb = 0
                remaining_lrb_size = lrb.size  # position in current lrb is 0
            return True

        next_lrb()

        while True:
            if not remaining_lrb_size:
                if not next_lrb():
                    break

            if remaining_lrb_size <= remaining_vr_space:
                current_vr_body += lrb.make_segment(start_pos=position_in_current_lrb)
                # size increased by: header (4 bytes), length of the added lrb tail, and padding (if the former is odd)
                current_vr_body_size = current_vr_body_size + hs + remaining_lrb_size + (remaining_lrb_size % 2)
                remaining_vr_space = max_vr_body_size - current_vr_body_size - hs
                if not next_lrb():
                    break

            else:
                segment_size = min(remaining_vr_space, remaining_lrb_size)
                future_remaining_lrb_size = remaining_lrb_size - segment_size
                if segment_size >= mbs and future_remaining_lrb_size >= mbs:
                    current_vr_body += lrb.make_segment(start_pos=position_in_current_lrb, n_bytes=segment_size)
                    current_vr_body_size += segment_size + hs
                    position_in_current_lrb += segment_size
                    remaining_lrb_size = future_remaining_lrb_size
                next_vr()

        output += self._make_visible_record(current_vr_body, size=current_vr_body_size)
        bar.finish()

        return output

    @staticmethod
    @log_progress("Writing to file...")
    def write_bytes_to_file(raw_bytes: bytes, filename: Union[str, bytes, os.PathLike]):
        """Writes the bytes to a DLIS file"""

        with open(filename, 'wb') as f:
            f.write(raw_bytes)

        logger.info(f"Data written to file: '{filename}'")

    @profile
    def write_dlis(self, logical_records: LogicalRecordCollection, filename: Union[str, bytes, os.PathLike]):
        """Top level method that calls all the other methods to create and write DLIS bytes"""

        logical_records.check_objects()

        self.assign_origin_reference(logical_records)
        all_lrb_iter = self.make_bytes_of_logical_records(logical_records)
        all_bytes = self.create_visible_records(len(logical_records), all_lrb_iter)
        self.write_bytes_to_file(all_bytes, filename)
        logger.info('DLIS file created.')
    