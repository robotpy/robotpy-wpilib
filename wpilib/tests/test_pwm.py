import pytest
from unittest.mock import MagicMock

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

def test_pwm_free(pwm, hal, wpilib):
    wasport = pwm._port
    assert pwm.port == pwm._port
    pwm.free()
    assert pwm.port is None
    hal.setPWM.assert_called_once_with(wasport, 0)
    hal.freePWMChannel.assert_called_once_with(wasport)
    hal.freeDIO.assert_called_once_with(wasport)
    # try to re-grab
    pwm2 = wpilib.PWM(2)

@pytest.mark.parametrize("value", [True, False])
def test_pwm_enableDeadbandElimination(value, pwm):
    pwm.enableDeadbandElimination(value)
    assert pwm.eliminateDeadband == value

def test_pwm_setBounds(pwm, hal, wpilib):
    hal.getLoopTiming.return_value = wpilib.SensorBase.kSystemClockTicksPerMicrosecond
    # use victor settings for test
    pwm.setBounds(2.027, 1.525, 1.507, 1.49, 1.026)
    assert pwm.maxPwm == 1526
    assert pwm.deadbandMaxPwm == 1024
    assert pwm.centerPwm == 1005
    assert pwm.deadbandMinPwm == 989
    assert pwm.minPwm == 525

@pytest.fixture(scope="function")
def boundpwm(pwm):
    # mock up with nice numeric values
    pwm.maxPwm = 1500
    pwm.deadbandMaxPwm = 1050
    pwm.centerPwm = 1000
    pwm.deadbandMinPwm = 950
    pwm.minPwm = 500
    return pwm

def test_pwm_getChannel(pwm):
    assert pwm.getChannel() == pwm.channel

@pytest.mark.parametrize("param,expected", [(0.5, 1000), (0.25, 750)])
def test_setPosition(param, expected, boundpwm, hal):
    boundpwm.setPosition(param)
    hal.setPWM.assert_called_once_with(boundpwm._port, expected)

@pytest.mark.parametrize("param,expected", [(1.5, 1500), (-0.5, 500)])
def test_setPosition_limits(param, expected, boundpwm, hal):
    boundpwm.setPosition(param)
    hal.setPWM.assert_called_once_with(boundpwm._port, expected)

@pytest.mark.parametrize("param,expected", [(1000, 0.5), (750, 0.25)])
def test_getPosition(param, expected, boundpwm, hal):
    hal.getPWM.return_value = param
    assert boundpwm.getPosition() == expected

@pytest.mark.parametrize("param,expected", [(1600, 1.0), (400, 0.0)])
def test_getPosition_limits(param, expected, boundpwm, hal):
    hal.getPWM.return_value = param
    assert boundpwm.getPosition() == expected

@pytest.mark.parametrize("db,param,expected",
        # no deadband elimination results in direct scaling from center
        [(False, 0.0, 1000), (False, 0.5, 1251), (False, -0.5, 750),
        # deadband elimination results in scaling from deadband edge
         (True, 0.0, 1000), (True, 0.5, 1275), (True, -0.5, 725)])
def test_setSpeed(db, param, expected, boundpwm, hal):
    boundpwm.eliminateDeadband = db
    boundpwm.setSpeed(param)
    hal.setPWM.assert_called_once_with(boundpwm._port, expected)

@pytest.mark.parametrize("param,expected", [(1.5, 1500), (-1.5, 500)])
def test_setSpeed_limits(param, expected, boundpwm, hal):
    boundpwm.setSpeed(param)
    hal.setPWM.assert_called_once_with(boundpwm._port, expected)

@pytest.mark.parametrize("db,param,expected",
        # no deadband elimination results in direct scaling from center
        [(False, 1251, 0.5), (False, 750, -0.5), (False, 1000, 0.0),
        # deadband elimination results in scaling from deadband edge
         (True, 1275, 0.5), (True, 725, -0.5),
        # deadband elimination also results in values within deadband = 0.0
         (True, 1050, 0.0), (True, 950, 0.0)])
def test_getSpeed(db, param, expected, boundpwm, hal):
    # no deadband elimination
    boundpwm.eliminateDeadband = db
    hal.getPWM.return_value = param
    assert round(boundpwm.getSpeed(), 2) == expected

@pytest.mark.parametrize("param,expected", [(1600, 1.0), (400, -1.0)])
def test_getSpeed_limits(param, expected, boundpwm, hal):
    hal.getPWM.return_value = param
    assert boundpwm.getSpeed() == expected

def test_pwm_setRaw(pwm, hal):
    pwm.setRaw(60)
    hal.setPWM.assert_called_once_with(pwm._port, 60)

def test_pwm_setRaw_freed(pwm, hal):
    pwm.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        pwm.setRaw(60)
    assert not hal.setPWM.called

def test_pwm_getRaw(pwm, hal):
    assert pwm.getRaw() == hal.getPWM.return_value
    hal.getPWM.assert_called_once_with(pwm._port)

def test_pwm_getRaw_freed(pwm, hal):
    pwm.free()
    hal.reset_mock()
    with pytest.raises(ValueError):
        pwm.getRaw()
    assert not hal.getPWM.called

@pytest.mark.parametrize("param,expected", [("k4X", 3), ("k2X", 1), ("k1X", 0)])
def test_pwm_setPeriodMultiplier(param, expected, pwm, hal):
    pwm.setPeriodMultiplier(getattr(pwm.PeriodMultiplier, param))
    hal.setPWMPeriodScale.assert_called_once_with(pwm._port, expected)

def test_pwm_setPeriodMultiplier_freed(pwm, hal):
    pwm.free()
    with pytest.raises(ValueError):
        pwm.setPeriodMultiplier(pwm.PeriodMultiplier.k4X)
    assert not hal.setPWMperiodScale.called

def test_pwm_setPeriodMultiplier_badvalue(pwm, hal):
    with pytest.raises(ValueError):
        pwm.setPeriodMultiplier(5)
    assert not hal.setPWMperiodScale.called

def test_pwm_setZeroLatch(pwm, hal):
    pwm.setZeroLatch()
    hal.latchPWMZero.assert_called_once_with(pwm._port)

def test_pwm_setZeroLatch_freed(pwm, hal):
    pwm.free()
    with pytest.raises(ValueError):
        pwm.setZeroLatch()
    assert not hal.latchPWMZero.called

def test_pwm_getMaxPositivePwm(boundpwm):
    assert boundpwm.getMaxPositivePwm() == 1500

@pytest.mark.parametrize("db,expected", [(True, 1050), (False, 1001)])
def test_pwm_getMinPositivePwm(db, expected, boundpwm):
    boundpwm.eliminateDeadband = db
    assert boundpwm.getMinPositivePwm() == expected

def test_pwm_getCenterPwm(boundpwm):
    assert boundpwm.getCenterPwm() == 1000

@pytest.mark.parametrize("db,expected", [(True, 950), (False, 999)])
def test_pwm_getMaxNegativePwm(db, expected, boundpwm):
    boundpwm.eliminateDeadband = db
    assert boundpwm.getMaxNegativePwm() == expected

def test_pwm_getMinNegativePwm(boundpwm):
    assert boundpwm.getMinNegativePwm() == 500

@pytest.mark.parametrize("db,expected", [(True, 450), (False, 499)])
def test_pwm_getPositiveScaleFactor(db, expected, boundpwm):
    boundpwm.eliminateDeadband = db
    assert boundpwm.getPositiveScaleFactor() == expected

@pytest.mark.parametrize("db,expected", [(True, 450), (False, 499)])
def test_pwm_getNegativeScaleFactor(db, expected, boundpwm):
    boundpwm.eliminateDeadband = db
    assert boundpwm.getNegativeScaleFactor() == expected

@pytest.mark.parametrize("db,expected", [(True, 1000), (False, 1000)])
def test_pwm_getFullRangeScaleFactor(db, expected, boundpwm):
    boundpwm.eliminateDeadband = db
    assert boundpwm.getFullRangeScaleFactor() == expected

def test_pwm_getSmartDashboardType(pwm):
    assert pwm.getSmartDashboardType() == "Speed Controller"

def test_pwm_updateTable(pwm):
    pwm.getTable = MagicMock()
    pwm.getSpeed = MagicMock()
    # normal case
    pwm.updateTable()
    pwm.getTable.return_value.putNumber.assert_called_once_with("Value", pwm.getSpeed.return_value)
    # None case
    pwm.getTable.return_value = None
    pwm.updateTable()

def test_pwm_valueChanged(pwm):
    pwm.setSpeed = MagicMock()
    pwm.valueChanged(None, None, 0.5, None)
    pwm.setSpeed.assert_called_once_with(0.5)

