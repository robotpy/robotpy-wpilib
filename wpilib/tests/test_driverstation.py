import pytest
from unittest.mock import MagicMock, patch

#
# Module-specific Fixtures
#

@pytest.fixture(scope="function")
def dsmock(wpimock, halmock):
    with patch("wpilib.driverstation.threading") as mockthread:
        myds = wpimock.DriverStation.getInstance()
    halmock.reset_mock()
    return myds

@pytest.fixture(scope="function")
def ds(wpilib, hal_data):
    with patch("wpilib.driverstation.threading") as mockthread:
        myds = wpilib.DriverStation.getInstance()
    return myds


#
# Tests
#

def test_dup(wpilib):
    '''Don't allow creating a driverStation instance manually'''
    ds = wpilib.DriverStation.getInstance()
    
    with pytest.raises(ValueError):
        _ = wpilib.DriverStation()
    

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

def test_release(dsmock):
    assert dsmock.thread_keepalive
    dsmock.release()
    assert not dsmock.thread_keepalive

def test_task(dsmock, halmock):
    # exit function after one iteration
    def unalive(sem, mutex):
        assert sem == dsmock.packetDataAvailableSem
        dsmock.thread_keepalive = False
    halmock.takeMultiWait = unalive
    dsmock.getData = MagicMock()
    dsmock.task()
    assert dsmock.getData.called
    assert dsmock.dataSem.notify_all.called

def test_task_safetyCounter(dsmock, halmock):
    # exit function after 5 iterations
    class unalive:
        def __init__(self):
            self.count = 0
        def __call__(self, sem, mutex):
            self.count += 1
            if self.count >= 5:
                dsmock.thread_keepalive = False
    halmock.takeMultiWait = unalive()
    dsmock.getData = MagicMock()
    with patch("wpilib.driverstation.MotorSafety") as mocksafety:
        dsmock.task()
        assert mocksafety.checkMotors.called

@pytest.mark.parametrize("mode", ["Disabled", "Autonomous", "Teleop", "Test"])
def test_task_usermode(mode, dsmock, halmock):
    # exit function after one iteration
    def unalive(sem, mutex):
        dsmock.thread_keepalive = False
    halmock.takeMultiWait = unalive
    dsmock.getData = MagicMock()
    setattr(dsmock, "userIn"+mode, True)
    dsmock.task()
    assert getattr(halmock, "HALNetworkCommunicationObserveUserProgram"+mode).called

def test_waitForData(dsmock):
    dsmock.waitForData()
    dsmock.dataSem.wait.assert_called_once_with(None)

def test_waitForData_timeout(dsmock):
    dsmock.waitForData(5.0)
    dsmock.dataSem.wait.assert_called_once_with(5.0)

def test_getData(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.getData()
    assert dsmock.newControlData
    # TODO: check joystick values

def test_getBatteryVoltage(dsmock, halmock):
    assert dsmock.getBatteryVoltage() == halmock.getVinVoltage.return_value

def test_getStickAxis(dsmock):
    dsmock.joystickAxes[2][0] = 127
    assert dsmock.getStickAxis(2, 0) == 1.0
    dsmock.joystickAxes[0][1] = -128
    assert dsmock.getStickAxis(0, 1) == -1.0

def test_getStickAxis_limits(dsmock, halmock):
    with pytest.raises(IndexError):
        dsmock.getStickAxis(-1, 1)
    with pytest.raises(IndexError):
        dsmock.getStickAxis(dsmock.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        dsmock.getStickAxis(0, -1)
    with pytest.raises(IndexError):
        dsmock.getStickAxis(0, halmock.kMaxJoystickAxes)

def test_getStickPOV(dsmock):
    dsmock.joystickPOVs[2][0] = 30
    assert dsmock.getStickPOV(2, 0) == 30

def test_getStickPOV_limits(dsmock, halmock):
    with pytest.raises(IndexError):
        dsmock.getStickPOV(-1, 1)
    with pytest.raises(IndexError):
        dsmock.getStickPOV(dsmock.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        dsmock.getStickPOV(0, -1)
    with pytest.raises(IndexError):
        dsmock.getStickPOV(0, halmock.kMaxJoystickPOVs)

def test_getStickButton(dsmock):
    class ButtonsMock:
        buttons = 0x13
        count = 12
    dsmock.joystickButtons[0] = ButtonsMock()
    assert dsmock.getStickButton(0, 1) == True

def test_getStickButton_limits(dsmock):
    with pytest.raises(IndexError):
        dsmock.getStickButton(-1, 1)
    with pytest.raises(IndexError):
        dsmock.getStickButton(dsmock.kJoystickPorts, 1)

def test_getJoystickIsXbox(ds, hal_data):
    hal_data['joysticks'][0]['isXbox'] = True
    assert ds.getJoystickIsXbox(0)
    
    hal_data['joysticks'][1]['isXbox'] = False
    assert not ds.getJoystickIsXbox(1)

def test_getJoystickName(ds, hal_data):
    hal_data['joysticks'][0]['name'] = 'bob'
    assert ds.getJoystickName(0) == 'bob'

def test_isEnabled(dsmock, halmock):
    halmock.HALGetControlWord.return_value.enabled = 1
    assert dsmock.isEnabled()
    halmock.HALGetControlWord.return_value.enabled = 0
    assert not dsmock.isEnabled()

def test_isDisabled(dsmock, halmock):
    halmock.HALGetControlWord.return_value.enabled = 0
    assert dsmock.isDisabled()
    halmock.HALGetControlWord.return_value.enabled = 1
    assert not dsmock.isDisabled()

def test_isAutonomous(dsmock, halmock):
    halmock.HALGetControlWord.return_value.autonomous = 1
    assert dsmock.isAutonomous()
    halmock.HALGetControlWord.return_value.autonomous = 0
    assert not dsmock.isAutonomous()

def test_isTest(dsmock, halmock):
    halmock.HALGetControlWord.return_value.test = 1
    assert dsmock.isTest()
    halmock.HALGetControlWord.return_value.test = 0
    assert not dsmock.isTest()

@pytest.mark.parametrize("auto,test,oper",
        [(0, 0, True), (0, 1, False), (1, 0, False), (1, 1, False)])
def test_isOperatorControl(auto, test, oper, dsmock, halmock):
    halmock.HALGetControlWord.return_value.autonomous = auto
    halmock.HALGetControlWord.return_value.test = test
    assert dsmock.isOperatorControl() == oper

def test_isNewControlData(dsmock):
    dsmock.newControlData = False
    assert not dsmock.isNewControlData()
    dsmock.newControlData = True
    assert dsmock.isNewControlData()
    assert not dsmock.newControlData # verify it cleared the flag

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getAlliance(alliance, dsmock, halmock):
    if alliance != -1:
        result = getattr(dsmock.Alliance, alliance[:-1].title())
        alliance = getattr(halmock, "kHALAllianceStationID_"+alliance)
    else:
        result = dsmock.Alliance.Invalid
    halmock.HALGetAllianceStation.return_value = alliance
    assert dsmock.getAlliance() == result

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getLocation(alliance, dsmock, halmock):
    if alliance != -1:
        result = int(alliance[-1])
        alliance = getattr(halmock, "kHALAllianceStationID_"+alliance)
    else:
        result = 0
    halmock.HALGetAllianceStation.return_value = alliance
    assert dsmock.getLocation() == result

def test_isFMSAttached_mock(dsmock, halmock):
    halmock.HALGetControlWord.return_value.fmsAttached = 1
    assert dsmock.isFMSAttached()
    halmock.HALGetControlWord.return_value.fmsAttached = 0
    assert not dsmock.isFMSAttached()
    
def test_isFMSAttached(ds, hal_data):
    hal_data['control']['fms_attached'] = True
    assert ds.isFMSAttached()
    
    hal_data['control']['fms_attached'] = False
    assert not ds.isFMSAttached()

def test_getMatchTime(dsmock, halmock):
    assert dsmock.getMatchTime() == halmock.HALGetMatchTime.return_value

def test_InDisabled(dsmock):
    dsmock.InDisabled(True)
    assert dsmock.userInDisabled
    dsmock.InDisabled(False)
    assert not dsmock.userInDisabled

def test_InAutonomous(dsmock):
    dsmock.InAutonomous(True)
    assert dsmock.userInAutonomous
    dsmock.InAutonomous(False)
    assert not dsmock.userInAutonomous

def test_InOperatorControl(dsmock):
    dsmock.InOperatorControl(True)
    assert dsmock.userInTeleop
    dsmock.InOperatorControl(False)
    assert not dsmock.userInTeleop

def test_InTest(dsmock):
    dsmock.InTest(True)
    assert dsmock.userInTest
    dsmock.InTest(False)
    assert not dsmock.userInTest

