import pytest
from configparser import ConfigParser

from dlis_writer.logical_record.eflr_types.file_header import FileHeader, FileHeaderObject
from dlis_writer.tests.common import base_data_path, config_params, make_config


def _check_with_config(fh: FileHeaderObject, config: ConfigParser):
    """Check that identifier and sequence number of the file header match the ones specified in the config."""

    assert fh.identifier == config['FileHeader']['name']
    assert fh.sequence_number == int(config['FileHeader']['sequence_number'])


def test_from_config(config_params: ConfigParser):
    """Test creating a FileHeaderObject from config."""

    fh: FileHeaderObject = FileHeader.make_object_from_config(config_params)
    _check_with_config(fh, config_params)


@pytest.mark.parametrize(("identifier", "sequence_number"), (("a", "9"), ("123ert", "3")))
def test_from_config_with_params(identifier: str, sequence_number: str):
    """Test creating a FileHeaderObject from config with alternative values for the main parameters."""

    config = make_config("FileHeader")
    config["FileHeader"]["name"] = identifier
    config["FileHeader"]["sequence_number"] = sequence_number

    fh: FileHeaderObject = FileHeader.make_object_from_config(config)
    _check_with_config(fh, config)
