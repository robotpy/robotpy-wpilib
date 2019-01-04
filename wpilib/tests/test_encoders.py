import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def encoder_data(hal_data):
    return hal_data["encoder"][0]


@pytest.fixture(scope="function")
def encoder_table(networktables):
    return networktables.NetworkTables.getTable("/LiveWindow/Ungrouped/Encoder[1]")


# The simulated hal data for an encoder appears to be structured like this:
# ["initialized"] (bool)
# ["config"] (list)
# ["reverse_direction"] (bool)

# The config for an encoder appears to be a list ordered as follows:
# port_a_pin
# port_a_analog_trigger False
# port_b_pin
# port_b_analog_trigger False


def check_config(config, a_pin, a_atr, b_pin, b_atr):
    assert config["ASource_Channel"] == a_pin
    assert config["ASource_AnalogTrigger"] == a_atr
    assert config["BSource_Channel"] == b_pin
    assert config["BSource_AnalogTrigger"] == b_atr


def test_encoder_channel_channel_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == False
    x.close()
    assert encoder_data["initialized"] == False


def test_encoder_channel_channel_reverse_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, True)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    assert encoder_data["initialized"] == False


def test_encoder_channel_channel_reverse_type_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, True, wpilib.Encoder.EncodingType.k4X)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    assert encoder_data["initialized"] == False


def test_encoder_channel_channel_channel_reverse_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, 3, True)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    assert encoder_data["initialized"] == False


def test_encoder_channel_channel_channel_init(wpilib, encoder_data):
    x = wpilib.Encoder(1, 2, 3)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == False
    x.close()
    assert encoder_data["initialized"] == False


def test_encoder_source_source_reverse_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2, True)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    s1.close()
    s2.close()
    assert encoder_data["initialized"] == False


def test_encoder_source_source_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == False
    x.close()
    s1.close()
    s2.close()
    assert encoder_data["initialized"] == False


def test_encoder_source_source_reverse_type_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    x = wpilib.Encoder(s1, s2, True, wpilib.Encoder.EncodingType.k4X)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    s1.close()
    s2.close()
    assert encoder_data["initialized"] == False


def test_encoder_source_source_source_reverse_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    s3 = wpilib.DigitalInput(3)
    x = wpilib.Encoder(s1, s2, s3, True)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == True
    x.close()
    s1.close()
    s2.close()
    s3.close()
    assert encoder_data["initialized"] == False


def test_encoder_source_source_source_init(wpilib, encoder_data):
    s1 = wpilib.DigitalInput(1)
    s2 = wpilib.DigitalInput(2)
    s3 = wpilib.DigitalInput(3)
    x = wpilib.Encoder(s1, s2, s3)
    assert encoder_data["initialized"] == True
    check_config(encoder_data["config"], 1, False, 2, False)
    assert encoder_data["reverse_direction"] == False
    x.close()
    s1.close()
    s2.close()
    s3.close()
    assert encoder_data["initialized"] == False


def test_encoder_fpgaindex(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    # ?hal?
    # assert encoder.getFPGAIndex() == 1


def test_encoder_encodingscale(wpilib):
    encoder = wpilib.Encoder(1, 2)

    # ?hal?
    # assert encoder.getEncodingScale() == 1


def test_encoder_getRaw(wpilib):
    encoder = wpilib.Encoder(1, 2)

    # ?hal?
    # assert encoder.getRaw() == 1


def test_encoder_get(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder_data["count"] = 11
    assert encoder.get() == 11


def test_encoder_reset(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder_data["count"] = 11
    encoder.reset()
    assert encoder.get() == 0


def test_encoder_setMaxPeriod(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder.setMaxPeriod(0.2)
    assert encoder_data["max_period"] == pytest.approx(0.2, 0.01)


def test_encoder_stopped(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder.setMaxPeriod(0.2)
    encoder_data["period"] = 0.1
    assert encoder.getStopped() == False
    encoder_data["period"] = 0.3
    assert encoder.getStopped() == True


def test_encoder_getRate(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)
    encoder.setDistancePerPulse(2.1)

    encoder_data["rate"] = 3.0
    assert encoder.getRate() == pytest.approx(6.3, 0.01)


def test_encoder_setMinRate(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder.setMinRate(0.1)
    assert encoder_data["min_rate"] == pytest.approx(0.1, 0.01)


def test_encoder_getDistance(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)

    encoder.setDistancePerPulse(2.1)
    encoder_data["count"] = 2.0
    assert encoder.getDistance() == pytest.approx(4.2, 0.01)


def test_encoder_setReverseDirection(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)
    encoder.setReverseDirection(True)
    assert encoder_data["reverse_direction"] == True


def test_encoder_samplesToAverage(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)
    encoder.setSamplesToAverage(17)
    assert encoder.getSamplesToAverage() == 17


def test_encoder_pidget_displacement1(wpilib):
    encoder = wpilib.Encoder(1, 2)
    encoder.setDistancePerPulse(1.0)
    encoder.getDistance = MagicMock(return_value=4.4)

    encoder.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kDisplacement)

    assert encoder.pidGet() == pytest.approx(4.4, 0.01)


def test_encoder_pidget_displacement2(wpilib, encoder_data):
    encoder = wpilib.Encoder(1, 2)
    encoder.setDistancePerPulse(1.0)
    encoder_data["rate"] = 3.0
    encoder.setPIDSourceType(wpilib.interfaces.PIDSource.PIDSourceType.kRate)
    assert encoder.pidGet() == pytest.approx(3.0, 0.01)


def test_encoder_initSendable_setSmartDashboardType1(wpilib, sendablebuilder):
    encoder = wpilib.Encoder(1, 2, False, wpilib.Encoder.EncodingType.k2X)
    encoder.initSendable(sendablebuilder)

    assert sendablebuilder.getTable().getString(".type", "") == "Encoder"


def test_encoder_initSendable_setSmartDashboardType2(wpilib, sendablebuilder):
    encoder = wpilib.Encoder(1, 2, False, wpilib.Encoder.EncodingType.k4X)
    encoder.initSendable(sendablebuilder)

    assert sendablebuilder.getTable().getString(".type", "") == "Quadrature Encoder"


def test_encoder_initSendable_update(wpilib, encoder_data, sendablebuilder):
    encoder = wpilib.Encoder(1, 2)

    encoder_data["rate"] = 3.3
    encoder_data["count"] = 2.0
    encoder.setDistancePerPulse(2.1)

    encoder.initSendable(sendablebuilder)
    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Speed", 0.0) == pytest.approx(
        6.93, 0.01
    )
    assert sendablebuilder.getTable().getNumber("Distance", 0.0) == pytest.approx(
        4.2, 0.01
    )
    assert sendablebuilder.getTable().getNumber(
        "Distance per Tick", 0.0
    ) == pytest.approx(2.1, 0.01)
