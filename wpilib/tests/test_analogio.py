import pytest


@pytest.mark.parametrize("pin", range(8))
def test_analogin(wpilib, hal_data, pin):

    data = hal_data["analog_in"][pin]

    assert not data["initialized"]
    a = wpilib.AnalogInput(pin)
    assert data["initialized"]

    data["voltage"] = 5
    assert a.getVoltage() == 5
    data["voltage"] = 4
    assert a.getVoltage() == 4

    a.close()
    assert not data["initialized"]


@pytest.mark.parametrize("pin", range(2))
def test_analogout(wpilib, hal_data, pin):

    data = hal_data["analog_out"][pin]

    assert not data["initialized"]
    a = wpilib.AnalogOutput(pin)
    assert data["initialized"]

    data["voltage"] = 5
    a.setVoltage(5)
    assert data["voltage"] == 5.0

    a.close()
    assert not data["initialized"]


@pytest.mark.parametrize("pin", range(8))
def test_analogtrigger_init_close(wpilib, hal_data, pin):
    at = wpilib.AnalogTrigger(pin)
    assert hal_data["analog_trigger"][0]["initialized"]
    assert hal_data["analog_trigger"][0]["port"].pin == pin
    at.close()
    assert not hal_data["analog_trigger"][0]["initialized"]


def test_set_filtered(wpilib, hal_data):
    at = wpilib.AnalogTrigger(2)
    at.setFiltered(True)
    assert hal_data["analog_trigger"][0]["trig_type"] == "filtered"
