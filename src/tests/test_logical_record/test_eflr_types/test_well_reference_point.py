import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.well_reference_point import WellReferencePointTable, WellReferencePointItem

from tests.common import base_data_path, config_params


@pytest.mark.parametrize(("key", "name", "v_zero", "m_decl", "c1_name", "c1_value", "c2_name", "c2_value"), (
        ("1", "AQLN WELL-REF", "AQLN vertical_zero", 999.51, "Latitude", 40.395240, "Longitude", 27.792470),
        ("X", "WRP-X", "vz20", 112.3, "X", 20, "Y", -0.3)
))
def test_from_config(config_params: ConfigParser, key: str, name: str, v_zero: str, m_decl: float, c1_name: str,
                     c1_value: float, c2_name: str, c2_value: float):
    """Test creating WellReferencePoint from config."""

    key = f"WellReferencePoint-{key}"
    w: WellReferencePointItem = WellReferencePointTable.make_eflr_item_from_config(config_params, key=key)

    assert w.name == name
    assert w.vertical_zero.value == v_zero
    assert w.magnetic_declination.value == m_decl
    assert w.coordinate_1_name.value == c1_name
    assert w.coordinate_1_value.value == c1_value
    assert w.coordinate_2_name.value == c2_name
    assert w.coordinate_2_value.value == c2_value


