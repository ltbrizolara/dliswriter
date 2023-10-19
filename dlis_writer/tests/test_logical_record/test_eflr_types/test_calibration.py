from datetime import datetime

from dlis_writer.logical_record.eflr_types import (CalibrationMeasurement, CalibrationCoefficient, Calibration,
                                                   Channel, Axis, Parameter)
from dlis_writer.utils.enums import Units, RepresentationCode
from dlis_writer.tests.common import base_data_path, config_params, make_config


def test_calibration_measurement_from_config(config_params):
    key = "CalibrationMeasurement-1"
    m = CalibrationMeasurement.from_config(config_params, key=key)

    assert m.object_name == "CMEASURE-1"
    assert m.phase.value == 'BEFORE'
    assert isinstance(m.measurement_source.value, Channel)
    assert m.measurement_source.value.object_name == "Channel 1"
    assert m._type.value == 'Plus'
    assert isinstance(m.axis.value[0], Axis)
    assert m.axis.value[0].object_name == 'Axis-1'
    assert m.measurement.value == [12.2323]
    assert m.sample_count.value == [12]
    assert m.maximum_deviation.value == [2.2324]
    assert isinstance(m.begin_time.value, datetime)
    assert m.begin_time.value == datetime(2050, 3, 12, 12, 30)
    assert m.duration.value == 15
    assert m.duration.units is Units.s
    assert m.reference.value == [11]
    assert m.standard.value == [11.2]
    assert m.plus_tolerance.value == [2]
    assert m.minus_tolerance.value == [1]


def test_calibration_coefficient_from_config(config_params):
    key = "CalibrationCoefficient-1"
    c = CalibrationCoefficient.from_config(config_params, key=key)

    assert c.object_name == "COEF-1"
    assert c.label.value == 'Gain'
    assert c.coefficients.value == [100.2, 201.3]
    assert c.references.value == [89, 298]
    assert c.plus_tolerances.value == [100.2, 222.124]
    assert c.minus_tolerances.value == [87.23, 214]


def _check_list(objects, names, object_class):
    objects = objects.value

    assert isinstance(objects, list)
    assert len(objects) == len(names)
    for i, name in enumerate(names):
        assert isinstance(objects[i], object_class)
        assert objects[i].object_name == name


def test_calibration_from_config(config_params):
    key = "Calibration-1"
    c = Calibration.from_config(config_params, key=key)

    assert c.object_name == "CALIB-MAIN"

    _check_list(c.calibrated_channels, ("Channel 1", "Channel 2"), Channel)
    _check_list(c.uncalibrated_channels, ("amplitude", "radius", "radius_pooh"), Channel)
    _check_list(c.coefficients, ("COEF-1",), CalibrationCoefficient)
    _check_list(c.measurements, ("CMEASURE-1",), CalibrationMeasurement)
    _check_list(c.parameters, ("Param-1", "Param-2", "Param-3"), Parameter)
