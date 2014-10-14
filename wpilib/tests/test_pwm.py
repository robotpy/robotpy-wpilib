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

def test_pwm_allocate_error(hal, wpilib):
    hal.allocatePWMChannel.return_value = False
    with pytest.raises(IndexError):
        pwm = wpilib.PWM(5)

def test_pwm_create_limits(wpilib):
    with pytest.raises(IndexError):
        pwm = wpilib.PWM(-1)
    with pytest.raises(IndexError):
        pwm = wpilib.PWM(wpilib.SensorBase.kPwmChannels)

@pytest.fixture(scope="function")
def pwm(wpilib, hal):
    pwm = wpilib.PWM(2)
    hal.reset_mock()
    return pwm

def test_pwm_free(pwm, hal):
    wasport = pwm._port
    assert pwm.port == pwm._port
    pwm.free()
    assert pwm.port is None
    hal.setPWM.assert_called_once_with(wasport, 0)
    hal.freePWMChannel.assert_called_once_with(wasport)
    hal.freeDIO.assert_called_once_with(wasport)

def test_pwm_enableDeadbandElimination(pwm):
    pwm.enableDeadbandElimination(True)
    assert pwm.eliminateDeadband == True
    pwm.enableDeadbandElimination(False)
    assert pwm.eliminateDeadband == False

def test_pwm_getChannel(pwm):
    assert pwm.getChannel() == pwm.channel

def test_pwm_setRaw(pwm, hal):
    pwm.setRaw(60)
    hal.setPWM.assert_called_once_with(pwm._port, 60)

def test_pwm_setRaw_error(pwm, hal):
    pwm.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        pwm.setRaw(60)
    assert not hal.setPWM.called

def test_pwm_getRaw(pwm, hal):
    assert pwm.getRaw() == hal.getPWM.return_value
    hal.getPWM.assert_called_once_with(pwm._port)

def test_pwm_getRaw_error(pwm, hal):
    pwm.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        pwm.getRaw()
    assert not hal.getPWM.called

