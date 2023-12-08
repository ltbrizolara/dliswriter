import re
import logging
from typing import TYPE_CHECKING, Union

from dlis_writer.logical_record.core.logical_record import LRMeta

if TYPE_CHECKING:
    from dlis_writer.logical_record.core.eflr.eflr_table import EFLRTable


logger = logging.getLogger(__name__)


class EFLRTableMeta(LRMeta):
    """Define a metaclass for EFLRTable..

    The main motivation for defining this metaclass is to be able to use an instance dictionary (see _instance_dict
    in __new__), which is separate for each subclass of EFLRTable.

    In addition, this metaclass implements several class methods of EFLRTable, mostly related to creating EFLRTable
    and EFLRItem instances, e.g. from a config object.
    """

    _eflr_table_instance_dict: dict[Union[str, None], "EFLRTable"]
    item_type: type
    eflr_name: str
    eflr_name_pattern = re.compile(r'(?P<name>\w+)Table')

    def __new__(cls, *args, **kwargs) -> "EFLRTableMeta":
        """Create a new EFLRTable class (instance of EFLRMeta).

        All positional and keyword arguments are passed to the super-metaclass: LRMeta.
        """

        obj = super().__new__(cls, *args, **kwargs)
        obj._eflr_table_instance_dict = {}
        obj.eflr_name = cls.eflr_name_pattern.fullmatch(obj.__name__).group('name')
        return obj
