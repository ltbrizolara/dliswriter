from dlis_writer.logical_record.eflr_types.frame import FrameObject
from dlis_writer.logical_record.iflr_types import FrameData
from dlis_writer.utils.source_data_objects import SourceDataObject


class MultiFrameData:
    def __init__(self, frame: FrameObject, data: SourceDataObject, chunk_rows=None):
        super().__init__()

        frame_channel_names = tuple(c.name for c in frame.channels.value)
        data_channel_names = data.dtype.names
        if frame_channel_names != data_channel_names:
            raise ValueError(f"Channel names in data {data_channel_names} "
                             f"do not match channels defined in the frame {frame_channel_names}")

        self._data_source = data  # TODO: check with channel names of the frame
        self._frame = frame

        self._origin_reference = None

        self._chunk_rows = chunk_rows
        self._i = 0
        self._data_item_generator = None

    def set_origin_reference(self, value):
        self._origin_reference = value

    def _make_frame_data(self, idx: int):
        return FrameData(
            frame=self._frame,
            frame_number=idx + 1,
            slots=self._data_source[idx],
            origin_reference=self._origin_reference
        )

    def __len__(self):
        return self._data_source.n_rows

    def __iter__(self):
        self._i = 0
        self._data_item_generator = self._data_source.make_chunked_generator(chunk_rows=self._chunk_rows)
        return self

    def __next__(self):
        if self._i >= self._data_source.n_rows:
            raise StopIteration

        self._i += 1

        return FrameData(
            frame=self._frame,
            frame_number=self._i,
            slots=next(self._data_item_generator),
            origin_reference=self._origin_reference
        )
