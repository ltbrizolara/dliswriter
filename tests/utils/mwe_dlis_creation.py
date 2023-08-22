from datetime import datetime
from pathlib import Path
import numpy as np
import h5py
import os
import logging
from line_profiler_pycharm import profile

from logical_record.file import DLISFile
from logical_record.storage_unit_label import StorageUnitLabel
from logical_record.file_header import FileHeader
from logical_record.origin import Origin
from logical_record.frame import Frame
from logical_record.frame_data import MultiFrameData
from logical_record.utils.enums import Units, RepresentationCode
from logical_record.channel import make_channel
from tests.utils.make_mock_data_hdf5 import create_data


logger = logging.getLogger(__name__)


def make_origin():
    # ORIGIN
    origin = Origin('DEFINING ORIGIN')
    origin.file_id.value = 'WELL ID'
    origin.file_set_name.value = 'Test file set name'
    origin.file_set_number.value = 1
    origin.file_number.value = 0

    origin.creation_time.value = datetime(year=2050, month=3, day=2, hour=15, minute=30)

    origin.run_number.value = 1
    origin.well_id.value = 0
    origin.well_name.value = 'Test well name'
    origin.field_name.value = 'Test field name'
    origin.company.value = 'Test company'

    return origin


def load_h5_data(data_file_name, key='contents'):
    h5_data = h5py.File(data_file_name, 'r')[f'/{key}/']

    dtype = []
    arrays = []
    n_rows = None
    for key in h5_data.keys():
        key_data = h5_data.get(key)[:]
        arrays.append(key_data)

        dt = (key, key_data.dtype)
        if key_data.ndim > 1:
            dt = (*dt, key_data.shape[-1])
        dtype.append(dt)

        if n_rows is None:
            n_rows = key_data.shape[0]
        else:
            if n_rows != key_data.shape[0]:
                raise RuntimeError(
                    "Datasets in the file have different lengths; the data cannot be transformed to DLIS format")

    full_data = np.zeros(n_rows, dtype=dtype)
    for key, arr in zip(h5_data.keys(), arrays):
        full_data[key] = arr

    return full_data


@profile
def make_channels_and_frame(data: np.ndarray):
    # CHANNELS & FRAME
    frame = Frame('MAIN')
    frame.channels.value = [
        make_channel('posix time', unit='s', data=data['time']),
        make_channel('depth', unit='m', data=data['depth']),
        make_channel('surface rpm', unit='rpm', data=data['rpm']),
    ]

    if 'image' in data.dtype.names:
        n_cols = data['image'].shape[-1]
        frame.channels.value.append(
            make_channel('image', unit='m', data=data['image'], dimension=n_cols, element_limit=n_cols)
        )

    frame.index_type.value = 'TIME'
    frame.spacing.representation_code = RepresentationCode.FDOUBL
    frame.spacing.units = Units.s

    n_points = data.shape[0]
    logger.info(f'Preparing frames for {n_points} rows.')
    multi_frame_data = MultiFrameData(frame, data)

    return frame, multi_frame_data

@profile
def write_dlis_file(data, dlis_file_name):
    # CREATE THE FILE
    dlis_file = DLISFile(
        storage_unit_label=StorageUnitLabel(),
        file_header=FileHeader(),
        origin=make_origin()
    )

    frame, data_logical_records = make_channels_and_frame(data)

    meta_logical_records = [
        *frame.channels.value,
        frame
    ]

    dlis_file.write_dlis(meta_logical_records, data_logical_records, dlis_file_name)


if __name__ == '__main__':
    output_file_name = Path(__file__).resolve().parent.parent/'outputs/mwe_fake_dlis.DLIS'
    os.makedirs(output_file_name.parent, exist_ok=True)

    write_dlis_file(data=create_data(int(10e3), add_2d=True), dlis_file_name=output_file_name)
