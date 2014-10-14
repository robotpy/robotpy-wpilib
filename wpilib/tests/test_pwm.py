import pytest

def test_pwm_create(hal, wpilib):
    pwm = wpilib.PWM(5)
    hal.getPort.assert_called_once_with(5)
    hal.initializeDigitalPort.assert_called_once_with(hal.getPort.return_value)
    assert pwm.channel == 5
    assert pwm._port == hal.initializeDigitalPort.return_value
    hal.allocatePWMChannel.assert_called_once_with(pwm._port)
    hal.setPWM.assert_called_once_with(pwm._port, 0)
    assert pwm.eliminateDeadband == False
    hal.HALReport.assert_called_once_with(hal.HALUsageReporting.kResourceType_PWM, pwm.channel)

def test_pwm_create_limits(wpilib):
    with pytest.raises(IndexError):
        pwm = wpilib.PWM(-1)
    with pytest.raises(IndexError):
        pwm = wpilib.PWM(wpilib.SensorBase.kPwmChannels)

@pytest.fixture(scope="function")
def pwm(wpilib):
    return wpilib.PWM(0)

def test_pwm_free(pwm):
    pwm.free()
    assert pwm.port is None

def test_pwm_enableDeadbandElimination(pwm):
    pwm.enableDeadbandElimination(True)
    assert pwm.eliminateDeadband == True
    pwm.enableDeadbandElimination(False)
    assert pwm.eliminateDeadband == False
