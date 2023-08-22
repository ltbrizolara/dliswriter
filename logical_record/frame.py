from .utils.core import EFLR


class Frame(EFLR):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.logical_record_type = 'FRAME'
        self.set_type = 'FRAME'

        self.description = None
        self.channels = None
        self.index_type = None
        self.direction = None
        self.spacing = None
        self.encrypted = None
        self.index_min = None
        self.index_max = None

        self.create_attributes()

    @property
    def key(self):
        return hash(type(self))

