import pytest
from unittest.mock import MagicMock, patch

#
# Module-specific Fixtures
#

@pytest.fixture(scope="function")
def ds(wpimock, halmock):
    with patch("wpilib.driverstation.threading") as mockthread:
        myds = wpimock.DriverStation.getInstance()
    halmock.reset_mock()
    return myds

#
# Tests
#

def test_init(wpimock, halmock):
    with patch("wpilib.driverstation.threading") as mockthread:
        ds = wpimock.DriverStation.getInstance()
        assert mockthread.Thread.called
        assert mockthread.Thread.return_value.daemon == True
        assert mockthread.Thread.return_value.start.called
        assert ds.mutex == mockthread.RLock.return_value
        mockthread.Condition.assert_called_once_with(ds.mutex)
        assert ds.dataSem == mockthread.Condition.return_value
    assert ds.packetDataAvailableMutex == halmock.initializeMutexNormal.return_value
    assert ds.packetDataAvailableSem == halmock.initializeMultiWait.return_value
    halmock.HALSetNewDataSem.assert_called_once_with(ds.packetDataAvailableSem)
    assert ds.userInDisabled == False
    assert ds.userInAutonomous == False
    assert ds.userInTeleop == False
    assert ds.userInTest == False
    assert ds.newControlData == False
    assert ds.thread_keepalive == True

def test_release(ds):
    assert ds.thread_keepalive
    ds.release()
    assert not ds.thread_keepalive

def test_task(ds, halmock):
    # exit function after one iteration
    def unalive(sem, mutex, timeout):
        assert sem == ds.packetDataAvailableSem
        ds.thread_keepalive = False
    halmock.takeMultiWait = unalive
    ds.task()
    assert ds.newControlData
    assert ds.dataSem.notify_all.called

def test_task_safetyCounter(ds, halmock):
    # exit function after 5 iterations
    class unalive:
        def __init__(self):
            self.count = 0
        def __call__(self, sem, mutex, timeout):
            self.count += 1
            if self.count >= 5:
                ds.thread_keepalive = False
    halmock.takeMultiWait = unalive()
    with patch("wpilib.driverstation.MotorSafety") as mocksafety:
        ds.task()
        assert mocksafety.checkMotors.called

@pytest.mark.parametrize("mode", ["Disabled", "Autonomous", "Teleop", "Test"])
def test_task_usermode(mode, ds, halmock):
    # exit function after one iteration
    def unalive(sem, mutex, timeout):
        ds.thread_keepalive = False
    halmock.takeMultiWait = unalive
    setattr(ds, "userIn"+mode, True)
    ds.task()
    assert getattr(halmock, "HALNetworkCommunicationObserveUserProgram"+mode).called

def test_waitForData(ds):
    ds.waitForData()
    ds.dataSem.wait.assert_called_once_with(None)

def test_waitForData_timeout(ds):
    ds.waitForData(5.0)
    ds.dataSem.wait.assert_called_once_with(5.0)

def test_getBatteryVoltage(ds, halmock):
    assert ds.getBatteryVoltage() == halmock.getVinVoltage.return_value

@pytest.mark.parametrize("stick,axis,value", [(2, 0, 127), (0, 1, -128)])
def test_getStickAxis(ds, halmock, stick, axis, value):
    axes = [0]*axis
    axes.append(value)
    halmock.HALGetJoystickAxes.return_value = axes
    expect = value / 127.0 if value >= 0 else value / 128.0
    assert ds.getStickAxis(stick, axis) == expect
    halmock.HALGetJoystickAxes.assert_called_once_with(stick)

def test_getStickAxis_limits(ds, halmock):
    with pytest.raises(IndexError):
        ds.getStickAxis(-1, 1)
    with pytest.raises(IndexError):
        ds.getStickAxis(ds.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        ds.getStickAxis(0, -1)
    with pytest.raises(IndexError):
        ds.getStickAxis(0, halmock.kMaxJoystickAxes)

def test_getStickPOV(ds, halmock):
    halmock.HALGetJoystickPOVs.return_value = [30]
    assert ds.getStickPOV(2, 0) == 30
    halmock.HALGetJoystickPOVs.assert_called_once_with(2)

def test_getStickPOV_limits(ds, halmock):
    with pytest.raises(IndexError):
        ds.getStickPOV(-1, 1)
    with pytest.raises(IndexError):
        ds.getStickPOV(ds.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        ds.getStickPOV(0, -1)
    with pytest.raises(IndexError):
        ds.getStickPOV(0, halmock.kMaxJoystickPOVs)

def test_getStickButton(ds, halmock):
    halmock.HALGetJoystickButtons.return_value.buttons = 0x11
    halmock.HALGetJoystickButtons.return_value.count = 12
    assert ds.getStickButton(0, 1) == True
    halmock.HALGetJoystickButtons.assert_called_once_with(0)

def test_getStickButton_limits(ds):
    with pytest.raises(IndexError):
        ds.getStickButton(-1, 1)
    with pytest.raises(IndexError):
        ds.getStickButton(ds.kJoystickPorts, 1)

def test_isEnabled(ds, halmock):
    halmock.HALGetControlWord.return_value.enabled = 1
    assert ds.isEnabled()
    halmock.HALGetControlWord.return_value.enabled = 0
    assert not ds.isEnabled()

def test_isDisabled(ds, halmock):
    halmock.HALGetControlWord.return_value.enabled = 0
    assert ds.isDisabled()
    halmock.HALGetControlWord.return_value.enabled = 1
    assert not ds.isDisabled()

def test_isAutonomous(ds, halmock):
    halmock.HALGetControlWord.return_value.autonomous = 1
    assert ds.isAutonomous()
    halmock.HALGetControlWord.return_value.autonomous = 0
    assert not ds.isAutonomous()

def test_isTest(ds, halmock):
    halmock.HALGetControlWord.return_value.test = 1
    assert ds.isTest()
    halmock.HALGetControlWord.return_value.test = 0
    assert not ds.isTest()

@pytest.mark.parametrize("auto,test,oper",
        [(0, 0, True), (0, 1, False), (1, 0, False), (1, 1, False)])
def test_isOperatorControl(auto, test, oper, ds, halmock):
    halmock.HALGetControlWord.return_value.autonomous = auto
    halmock.HALGetControlWord.return_value.test = test
    assert ds.isOperatorControl() == oper

def test_isNewControlData(ds):
    ds.newControlData = False
    assert not ds.isNewControlData()
    ds.newControlData = True
    assert ds.isNewControlData()
    assert not ds.newControlData # verify it cleared the flag

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getAlliance(alliance, ds, halmock):
    if alliance != -1:
        result = getattr(ds.Alliance, alliance[:-1].title())
        alliance = getattr(halmock, "kHALAllianceStationID_"+alliance)
    else:
        result = ds.Alliance.Invalid
    halmock.HALGetAllianceStation.return_value = alliance
    assert ds.getAlliance() == result

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getLocation(alliance, ds, halmock):
    if alliance != -1:
        result = int(alliance[-1])
        alliance = getattr(halmock, "kHALAllianceStationID_"+alliance)
    else:
        result = 0
    halmock.HALGetAllianceStation.return_value = alliance
    assert ds.getLocation() == result

def test_isFMSAttached(ds, halmock):
    halmock.HALGetControlWord.return_value.fmsAttached = 1
    assert ds.isFMSAttached()
    halmock.HALGetControlWord.return_value.fmsAttached = 0
    assert not ds.isFMSAttached()

def test_getMatchTime(ds, halmock):
    assert ds.getMatchTime() == halmock.HALGetMatchTime.return_value

def test_InDisabled(ds):
    ds.InDisabled(True)
    assert ds.userInDisabled
    ds.InDisabled(False)
    assert not ds.userInDisabled

def test_InAutonomous(ds):
    ds.InAutonomous(True)
    assert ds.userInAutonomous
    ds.InAutonomous(False)
    assert not ds.userInAutonomous

def test_InOperatorControl(ds):
    ds.InOperatorControl(True)
    assert ds.userInTeleop
    ds.InOperatorControl(False)
    assert not ds.userInTeleop

def test_InTest(ds):
    ds.InTest(True)
    assert ds.userInTest
    ds.InTest(False)
    assert not ds.userInTest

