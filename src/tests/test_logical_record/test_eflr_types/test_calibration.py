import pytest
from datetime import datetime

from dlis_writer.logical_record.eflr_types.calibration import (CalibrationMeasurementItem,
                                                               CalibrationCoefficientItem, CalibrationItem)
from dlis_writer.logical_record.eflr_types.channel import ChannelItem
from dlis_writer.logical_record.eflr_types.axis import AxisItem
from dlis_writer.logical_record.eflr_types.parameter import ParameterItem
from dlis_writer.logical_record.core.attribute import EFLRAttribute


@pytest.fixture
def channel1():
    return ChannelItem("Channel 1")


@pytest.fixture
def channel2():
    return ChannelItem("Channel 2")


@pytest.fixture
def channel3():
    return ChannelItem("Channel 3")


@pytest.fixture
def ccoef1():
    return CalibrationCoefficientItem("COEF-1")


@pytest.fixture
def cmeasure1():
    return CalibrationMeasurementItem("CMEASURE-1")


@pytest.fixture
def axis1():
    return AxisItem("Axis-1")


@pytest.fixture
def param1():
    return ParameterItem("Param-1")


@pytest.fixture
def param2():
    return ParameterItem("Param-2")


@pytest.fixture
def param3():
    return ParameterItem("Param-3")



def test_calibration_measurement_creation(channel1, axis1):
    m = CalibrationMeasurementItem(
        "CMEASURE-1",
        **{
            'phase': 'BEFORE',
            'measurement_source': channel1,
            '_type': 'Plus',
            'axis.value': axis1,
            'measurement.value': 12.2323,
            'sample_count.value': 12,
            'maximum_deviation': 2.2324,
            'begin_time': '2050/03/12 12:30:00',
            'duration': 15,
            'duration.units': 's',
            'reference': [11],
            'standard.value': [11.2],
            'plus_tolerance': [2],
            'minus_tolerance.value': 1
        }
    )

    assert m.name == "CMEASURE-1"
    assert m.phase.value == 'BEFORE'
    assert isinstance(m.measurement_source.value, ChannelItem)
    assert m.measurement_source.value.name == "Channel 1"
    assert m._type.value == 'Plus'
    assert isinstance(m.axis.value[0], AxisItem)
    assert m.axis.value[0].name == 'Axis-1'
    assert m.measurement.value == [12.2323]
    assert m.sample_count.value == 12
    assert m.maximum_deviation.value == 2.2324
    assert isinstance(m.begin_time.value, datetime)
    assert m.begin_time.value == datetime(2050, 3, 12, 12, 30)
    assert m.duration.value == 15
    assert m.duration.units == 's'
    assert m.reference.value == [11]
    assert m.standard.value == [11.2]
    assert m.plus_tolerance.value == [2]
    assert m.minus_tolerance.value == [1]


def test_calibration_coefficient_creation():
    """Check that a CalibrationCoefficientObject is correctly set up from config info."""

    c = CalibrationCoefficientItem(
        'COEF-1',
        label='Gain',
        coefficients=[100.2, 201.3],
        references=[89, 298],
        plus_tolerances=[100.2, 222.124],
        minus_tolerances=[87.23, 214],
    )

    assert c.name == "COEF-1"
    assert c.label.value == 'Gain'
    assert c.coefficients.value == [100.2, 201.3]
    assert c.references.value == [89, 298]
    assert c.plus_tolerances.value == [100.2, 222.124]
    assert c.minus_tolerances.value == [87.23, 214]


def _check_list(objects: EFLRAttribute, names: tuple[str, ...], object_class: type):
    """Check that the objects defined for a given EFLR attribute match the expected names and type."""

    objects = objects.value

    assert isinstance(objects, list)
    assert len(objects) == len(names)
    for i, name in enumerate(names):
        assert isinstance(objects[i], object_class)
        assert objects[i].name == name


def test_calibration_creation(channel1, channel2, channel3, ccoef1, cmeasure1, param1, param2, param3):
    """Check that a CalibrationObject is correctly set up from config info."""

    c = CalibrationItem(
        "CALIB-MAIN",
        calibrated_channels=(channel1, channel2),
        uncalibrated_channels=(channel3,),
        coefficients=(ccoef1,),
        measurements=(cmeasure1,),
        parameters=(param1, param2, param3)
    )

    assert c.name == "CALIB-MAIN"

    _check_list(c.calibrated_channels, ("Channel 1", "Channel 2"), ChannelItem)
    _check_list(c.uncalibrated_channels, ("Channel 3",), ChannelItem)
    _check_list(c.coefficients, ("COEF-1",), CalibrationCoefficientItem)
    _check_list(c.measurements, ("CMEASURE-1",), CalibrationMeasurementItem)
    _check_list(c.parameters, ("Param-1", "Param-2", "Param-3"), ParameterItem)
