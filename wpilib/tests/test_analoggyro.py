import pytest

import hal


@pytest.mark.parametrize("pin", range(2))
def test_analog_gyro(wpilib, hal_data, pin):

    data = hal_data["analog_gyro"][pin]

    assert not data["initialized"]

    gyro = wpilib.AnalogGyro(pin)
    assert data["initialized"]

    assert gyro.getAngle() == 0.0

    data["angle"] = 90.0
    assert gyro.getAngle() == 90.0


@pytest.mark.parametrize("pin", range(2, 8))
def test_analog_gyro_bad(wpilib, pin):
    with pytest.raises(hal.HALError):
        wpilib.AnalogGyro(pin)

    # with pytest.raises():
