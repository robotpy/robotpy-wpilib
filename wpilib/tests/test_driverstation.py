import pytest
from unittest.mock import MagicMock, patch

def test_init(wpilib, hal):
    with patch("wpilib.driverstation.threading") as mockthread:
        ds = wpilib.DriverStation.getInstance()
        assert mockthread.Thread.called
        assert mockthread.Thread.return_value.daemon == True
        assert mockthread.Thread.return_value.start.called
        assert ds.mutex == mockthread.RLock.return_value
        mockthread.Condition.assert_called_once_with(ds.mutex)
        assert ds.dataSem == mockthread.Condition.return_value
    assert ds.packetDataAvailableSem == hal.initializeMutexNormal.return_value
    hal.HALSetNewDataSem.assert_called_once_with(ds.packetDataAvailableSem)
    assert ds.controlWord == hal.HALControlWord.return_value
    assert ds.allianceStationID == -1
    assert ds.approxMatchTimeOffset == -1.0
    assert ds.userInDisabled == False
    assert ds.userInAutonomous == False
    assert ds.userInTeleop == False
    assert ds.userInTest == False
    assert ds.newControlData == False
    assert ds.thread_keepalive == True

@pytest.fixture(scope="function")
def ds(wpilib, hal):
    with patch("wpilib.driverstation.threading") as mockthread:
        myds = wpilib.DriverStation.getInstance()
    hal.reset_mock()
    return myds

def test_release(ds):
    assert ds.thread_keepalive
    ds.release()
    assert not ds.thread_keepalive

def test_task(ds, hal):
    # exit function after one iteration
    def unalive(sem):
        assert sem == ds.packetDataAvailableSem
        ds.thread_keepalive = False
    hal.takeMutex = unalive
    ds.getData = MagicMock()
    ds.task()
    assert ds.getData.called
    assert ds.dataSem.notify_all.called

def test_task_safetyCounter(ds, hal):
    # exit function after 5 iterations
    class unalive:
        def __init__(self):
            self.count = 0
        def __call__(self, sem):
            self.count += 1
            if self.count >= 5:
                ds.thread_keepalive = False
    hal.takeMutex = unalive()
    ds.getData = MagicMock()
    with patch("wpilib.driverstation.MotorSafety") as mocksafety:
        ds.task()
        assert mocksafety.checkMotors.called

@pytest.mark.parametrize("mode", ["Disabled", "Autonomous", "Teleop", "Test"])
def test_task_usermode(mode, ds, hal):
    # exit function after one iteration
    def unalive(sem):
        ds.thread_keepalive = False
    hal.takeMutex = unalive
    ds.getData = MagicMock()
    setattr(ds, "userIn"+mode, True)
    ds.task()
    assert getattr(hal, "HALNetworkCommunicationObserveUserProgram"+mode).called

def test_waitForData(ds):
    ds.waitForData()
    ds.dataSem.wait.assert_called_once_with(None)

def test_waitForData_timeout(ds):
    ds.waitForData(5.0)
    ds.dataSem.wait.assert_called_once_with(5.0)

def test_getData(ds, hal):
    hal.getFPGATime.return_value = 1000
    ds.getData()
    assert ds.controlWord == hal.HALGetControlWord.return_value
    assert ds.allianceStationID == hal.HALGetAllianceStation.return_value
    assert ds.newControlData
    # TODO: check joystick values

def test_getData_matchtime(ds, wpilib):
    with patch("wpilib.driverstation.Timer") as timermock:
        timermock.getFPGATimestamp.return_value = 17.0

        # in auto
        wpilib.DriverStation.lastEnabled = False
        ds.controlWord.enabled = True
        ds.controlWord.autonomous = True
        ds.getData()
        assert ds.approxMatchTimeOffset == 17.0

        # starting teleop
        wpilib.DriverStation.lastEnabled = False
        ds.controlWord.enabled = True
        ds.controlWord.autonomous = False
        ds.getData()
        assert ds.approxMatchTimeOffset == 2.0

        # disabling
        wpilib.DriverStation.lastEnabled = True
        ds.controlWord.enabled = False
        ds.getData()
        assert ds.approxMatchTimeOffset == -1.0

def test_getBatteryVoltage(ds, hal):
    assert ds.getBatteryVoltage() == hal.getVinVoltage.return_value

def test_getStickAxis(ds):
    ds.joystickAxes[2][0] = 127
    assert ds.getStickAxis(2, 1) == 1.0
    ds.joystickAxes[0][1] = -128
    assert ds.getStickAxis(0, 2) == -1.0

def test_getStickAxis_limits(ds, hal):
    with pytest.raises(IndexError):
        ds.getStickAxis(-1, 1)
    with pytest.raises(IndexError):
        ds.getStickAxis(ds.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        ds.getStickAxis(0, 0)
    with pytest.raises(IndexError):
        ds.getStickAxis(0, hal.kMaxJoystickAxes+1)

def test_getStickPOV(ds):
    ds.joystickPOVs[2][0] = 30
    assert ds.getStickPOV(2, 1) == 30

def test_getStickPOV_limits(ds, hal):
    with pytest.raises(IndexError):
        ds.getStickPOV(-1, 1)
    with pytest.raises(IndexError):
        ds.getStickPOV(ds.kJoystickPorts, 1)
    with pytest.raises(IndexError):
        ds.getStickPOV(0, 0)
    with pytest.raises(IndexError):
        ds.getStickPOV(0, hal.kMaxJoystickPOVs+1)

def test_getStickButtons(ds):
    ds.joystickButtons[0] = 0x13
    assert ds.getStickButtons(0) == 0x13

def test_getStickButtons_limits(ds):
    with pytest.raises(IndexError):
        ds.getStickButtons(-1)
    with pytest.raises(IndexError):
        ds.getStickButtons(ds.kJoystickPorts)

def test_isEnabled(ds):
    ds.controlWord.enabled = 1
    assert ds.isEnabled()
    ds.controlWord.enabled = 0
    assert not ds.isEnabled()

def test_isDisabled(ds):
    ds.controlWord.enabled = 0
    assert ds.isDisabled()
    ds.controlWord.enabled = 1
    assert not ds.isDisabled()

def test_isAutonomous(ds):
    ds.controlWord.autonomous = 1
    assert ds.isAutonomous()
    ds.controlWord.autonomous = 0
    assert not ds.isAutonomous()

def test_isTest(ds):
    ds.controlWord.test = 1
    assert ds.isTest()
    ds.controlWord.test = 0
    assert not ds.isTest()

@pytest.mark.parametrize("auto,test,oper",
        [(0, 0, True), (0, 1, False), (1, 0, False), (1, 1, False)])
def test_isOperatorControl(auto, test, oper, ds):
    ds.controlWord.autonomous = auto
    ds.controlWord.test = test
    assert ds.isOperatorControl() == oper

def test_isNewControlData(ds):
    ds.newControlData = False
    assert not ds.isNewControlData()
    ds.newControlData = True
    assert ds.isNewControlData()
    assert not ds.newControlData # verify it cleared the flag

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getAlliance(alliance, ds, hal):
    if alliance != -1:
        result = getattr(ds.Alliance, alliance[:-1].title())
        alliance = getattr(hal, "kHALAllianceStationID_"+alliance)
    else:
        result = ds.Alliance.Invalid
    ds.allianceStationID = alliance
    assert ds.getAlliance() == result

@pytest.mark.parametrize("alliance",
        ["red1", "red2", "red3", "blue1", "blue2", "blue3", -1])
def test_getLocation(alliance, ds, hal):
    if alliance != -1:
        result = int(alliance[-1])
        alliance = getattr(hal, "kHALAllianceStationID_"+alliance)
    else:
        result = 0
    ds.allianceStationID = alliance
    assert ds.getLocation() == result

def test_isFMSAttached(ds):
    ds.controlWord.fmsAttached = 1
    assert ds.isFMSAttached()
    ds.controlWord.fmsAttached = 0
    assert not ds.isFMSAttached()

def test_getMatchTime(ds):
    ds.approxMatchTimeOffset = -1.0
    assert ds.getMatchTime() == 0.0
    ds.approxMatchTimeOffset = 1.0
    with patch("wpilib.driverstation.Timer") as timermock:
        timermock.getFPGATimestamp.return_value = 2.0
        assert ds.getMatchTime() == 1.0

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

