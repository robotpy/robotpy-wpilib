import pytest
from unittest.mock import MagicMock

#
# Module-specific fixtures
#


@pytest.fixture(scope="function")
def pwm(wpilib):
    return wpilib.PWM(2)


@pytest.fixture(scope="function")
def pwm_data(hal_data):
    return hal_data["pwm"][2]


#
# Tests
#


def test_pwm_create(hal, hal_data, wpilib):
    assert hal_data["pwm"][5]["initialized"] == False
    pwm = wpilib.PWM(5)
    assert pwm.channel == 5
    assert pwm.channel in hal_data["reports"][hal.UsageReporting.kResourceType_PWM]
    assert hal_data["pwm"][5]["initialized"] == True


def test_pwm_allocate_error(wpilib, hal):
    _ = wpilib.PWM(5)
    with pytest.raises(hal.HALError):
        _ = wpilib.PWM(5)


def test_pwm_create_limits(wpilib):
    with pytest.raises(IndexError):
        _ = wpilib.PWM(-1)
    with pytest.raises(IndexError):
        _ = wpilib.PWM(wpilib.SensorUtil.kPwmChannels)


def test_pwm_create_all(wpilib):
    pwms = []
    for i in range(wpilib.SensorUtil.kPwmChannels):
        pwms.append(wpilib.PWM(i))


def test_pwm_close(pwm, pwm_data, wpilib, hal):
    pwm.close()

    with pytest.raises(hal.HALError):
        pwm.getSpeed()

    assert pwm_data["initialized"] == False

    # try to re-grab
    _ = wpilib.PWM(2)
    assert pwm_data["initialized"] == True


@pytest.mark.parametrize("value", [True, False])
def test_pwm_enableDeadbandElimination(value, pwm, pwm_data):
    pwm.enableDeadbandElimination(value)
    assert pwm_data["elim_deadband"] == value


def test_pwm_setBounds(pwm, hal_data, wpilib):
    hal_data["pwm_loop_timing"] = wpilib.SensorUtil.kSystemClockTicksPerMicrosecond
    # use victor settings for test
    pwm.setBounds(2.027, 1.525, 1.507, 1.49, 1.026)
    # TODO: someday store/convert the values
    # assert pwm.maxPwm == 1526
    # assert pwm.deadbandMaxPwm == 1024s
    # assert pwm.centerPwm == 1005
    # assert pwm.deadbandMinPwm == 989
    # assert pwm.minPwm == 525


def test_pwm_getChannel(pwm):
    assert pwm.getChannel() == pwm.channel


@pytest.mark.parametrize("param,expected", [(-2.0, 0), (0.5, 0.5), (2.0, 1.0)])
def test_position(param, expected, pwm, pwm_data):
    pwm.setPosition(param)
    assert pwm_data["value"] == expected
    assert pwm.getPosition() == expected


@pytest.mark.parametrize("param,expected", [(-2.0, -1.0), (0.5, 0.5), (2.0, 1.0)])
def test_speed(param, expected, pwm, pwm_data):
    pwm.setSpeed(param)
    assert pwm_data["value"] == expected
    assert pwm.getSpeed() == expected


def test_pwm_setRaw(pwm, pwm_data):
    pwm.setRaw(60)
    assert pwm_data["raw_value"] == 60


def test_pwm_setRaw_freed(hal, pwm, pwm_data):
    pwm.close()
    with pytest.raises(hal.HALError):
        pwm.setRaw(60)
    assert pwm_data["raw_value"] == 0


def test_pwm_getRaw(pwm, pwm_data):
    pwm_data["raw_value"] = 1234
    assert pwm.getRaw() == 1234


def test_pwm_getRaw_freed(hal, pwm):
    pwm.close()
    with pytest.raises(hal.HALError):
        pwm.getRaw()


@pytest.mark.parametrize("param,expected", [("k4X", 3), ("k2X", 1), ("k1X", 0)])
def test_pwm_setPeriodMultiplier(param, expected, pwm, pwm_data):
    pwm.setPeriodMultiplier(getattr(pwm.PeriodMultiplier, param))
    assert pwm_data["period_scale"] == expected


def test_pwm_setPeriodMultiplier_freed(hal, pwm, pwm_data):
    pwm.close()
    with pytest.raises(hal.HALError):
        pwm.setPeriodMultiplier(pwm.PeriodMultiplier.k4X)
    assert pwm_data["period_scale"] is None


def test_pwm_setPeriodMultiplier_badvalue(pwm, pwm_data):
    with pytest.raises(ValueError):
        pwm.setPeriodMultiplier(5)
    assert pwm_data["period_scale"] is None


def test_pwm_setZeroLatch(pwm, pwm_data):
    pwm.setZeroLatch()
    assert pwm_data["zero_latch"] == True


def test_pwm_setZeroLatch_freed(hal, pwm, pwm_data):
    pwm.close()
    with pytest.raises(hal.HALError):
        pwm.setZeroLatch()
    assert pwm_data["zero_latch"] == False
