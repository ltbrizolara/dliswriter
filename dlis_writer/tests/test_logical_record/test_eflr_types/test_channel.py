from dlis_writer.logical_record.eflr_types import Channel
from dlis_writer.utils.enums import RepresentationCode, Units
from dlis_writer.tests.common import base_data_path, config_params


def test_from_config(config_params):
    channel = Channel.from_config(config_params)

    assert channel.object_name == config_params['Channel']['name']
    assert channel.name == config_params['Channel']['name']

    conf = config_params['Channel.attributes']
    assert channel.long_name.value == conf["long_name"]
    assert channel.properties.value == ["property1", "property 2 with multiple words"]
    assert channel.representation_code.value is RepresentationCode.FSINGL
    assert channel.units.value is Units.acre
    assert channel.dimension.value == 12
    assert channel.axis.value == 'some axis'
    assert channel.element_limit.value == 12
    assert channel.source.value == 'some source'
    assert channel.minimum_value.value == 0.
    assert isinstance(channel.minimum_value.value, float)
    assert channel.maximum_value.value == 127.6


def test_from_config_alternative_name(config_params):
    channel = Channel.from_config(config_params, key="Channel-1")

    assert channel.object_name == "Channel 1"
    assert channel.name == "Channel 1"

    assert channel.dimension.value == 10
    assert channel.units.value == Units.in_


def test_properties():
    pass  # TODO


def test_dimension_and_element_limit():
    pass  # TODO


def test_multiple_channels_default_pattern(config_params):
    channels = Channel.all_from_config(config_params)

    assert len(channels) == 3
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"
    assert channels[2].name == "Channel 264"

    assert channels[0].dimension.value == 10
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value is None
    assert channels[1].units.value is None

    assert channels[2].element_limit.value == 128
    assert channels[2].units.value is None


def test_multiple_channels_custom_pattern(config_params):
    channels = Channel.all_from_config(config_params, key_pattern=r"Channel-\d")  # 1 digit only
    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Channel 2"

    assert channels[0].dimension.value == 10
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value is None
    assert channels[1].units.value is None


def test_multiple_channels_list(config_params):
    channels = Channel.all_from_config(config_params, keys=["Channel-1", "Channel"])

    assert len(channels) == 2
    assert channels[0].name == "Channel 1"
    assert channels[1].name == "Some Channel"

    assert channels[0].dimension.value == 10
    assert channels[0].units.value == Units.in_

    assert channels[1].dimension.value is 12
    assert channels[1].units.value is Units.acre
