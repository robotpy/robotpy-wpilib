import pytest

@pytest.mark.parametrize("pin", range(8))
def test_analogtrigger_init_free(wpilib, hal_data, pin):
    at = wpilib.AnalogTrigger(pin)
    assert hal_data["analog_trigger"][0]["initialized"]
    assert hal_data["analog_trigger"][0]["port"].pin == pin
    at.free()
    assert not hal_data["analog_trigger"][0]["initialized"]

def test_set_filtered(wpilib, hal_data):
    at = wpilib.AnalogTrigger(2)
    at.setFiltered(True)
    assert hal_data["analog_trigger"][0]["trig_type"] == "filtered"
