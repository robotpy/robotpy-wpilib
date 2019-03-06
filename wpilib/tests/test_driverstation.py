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
    """Don't allow creating a driverStation instance manually"""
    ds = wpilib.DriverStation.getInstance()

    with pytest.raises(ValueError):
        _ = wpilib.DriverStation()


def test_init(wpimock, halmock):
    with patch("wpilib.driverstation.threading") as mockthread:
        ds = wpimock.DriverStation.getInstance()
        assert mockthread.Thread.called
        assert mockthread.Thread.return_value.daemon == True
        assert mockthread.Thread.return_value.start.called
    assert ds.userInDisabled == False
    assert ds.userInAutonomous == False
    assert ds.userInTeleop == False
    assert ds.userInTest == False
    assert ds.threadKeepAlive == True


def test_release(dsmock):
    assert dsmock.threadKeepAlive
    dsmock.release()
    assert not dsmock.threadKeepAlive


def test_task(dsmock, halmock):
    # exit function after one iteration
    def unalive():
        dsmock.threadKeepAlive = False

    halmock.waitForDSData = unalive
    halmock.getFPGATime.return_value = 1000
    dsmock._getData = MagicMock()
    dsmock._run()
    assert dsmock._getData.called


def test_task_safetyCounter(dsmock, halmock):
    # exit function after 5 iterations
    class unalive:
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            if self.count >= 5:
                dsmock.threadKeepAlive = False

    halmock.getFPGATime.return_value = 1000
    halmock.waitForDSData = unalive()
    dsmock._getData = MagicMock()
    with patch("wpilib.driverstation.MotorSafety") as mocksafety:
        dsmock._run()
        assert mocksafety.checkMotors.called


@pytest.mark.parametrize("mode", ["Disabled", "Autonomous", "Teleop", "Test"])
def test_task_usermode(mode, dsmock, halmock):
    # exit function after one iteration
    def unalive():
        dsmock.threadKeepAlive = False

    halmock.getFPGATime.return_value = 1000
    halmock.waitForDSData = unalive
    dsmock._getData = MagicMock()
    setattr(dsmock, "userIn" + mode, True)
    dsmock._run()
    assert getattr(halmock, "observeUserProgram" + mode).called


def test_getData(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock._getData()
    # TODO: check joystick values


def test_getBatteryVoltage(dsmock, halmock):
    assert dsmock.getBatteryVoltage() == halmock.getVinVoltage.return_value


def test_getStickAxis(dsmock, halmock):
    dsmock.joystickAxes[2] = MagicMock()
    dsmock.joystickAxes[2].count = halmock.kMaxJoystickAxes
    dsmock.joystickAxes[2].axes = [1.0]
    assert dsmock.getStickAxis(2, 0) == 1.0
    dsmock.joystickAxes[0] = MagicMock()
    dsmock.joystickAxes[0].count = halmock.kMaxJoystickAxes
    dsmock.joystickAxes[0].axes = [0, -1.0]
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


def test_getStickPOV(dsmock, halmock):
    dsmock.joystickPOVs[2] = MagicMock()
    dsmock.joystickPOVs[2].count = halmock.kMaxJoystickPOVs
    dsmock.joystickPOVs[2].povs = [30]
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
    ds.joystickButtons[0] = MagicMock()
    ds.joystickButtons[0].count = 12
    hal_data["joysticks"][0]["isXbox"] = True
    assert ds.getJoystickIsXbox(0)

    ds.joystickButtons[1] = MagicMock()
    ds.joystickButtons[1].count = 12
    hal_data["joysticks"][1]["isXbox"] = False
    assert not ds.getJoystickIsXbox(1)


def test_getJoystickName(ds, hal_data):
    ds.joystickButtons[0] = MagicMock()
    ds.joystickButtons[0].count = 12
    hal_data["joysticks"][0]["name"] = "bob"
    assert ds.getJoystickName(0) == "bob"


def test_isEnabled(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.enabled = 1
    assert dsmock.isEnabled()
    dsmock.controlWordCache.enabled = 0
    assert not dsmock.isEnabled()


def test_isDisabled(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.enabled = 0
    assert dsmock.isDisabled()
    dsmock.controlWordCache.enabled = 1
    assert not dsmock.isDisabled()


def test_isAutonomous(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.autonomous = 1
    assert dsmock.isAutonomous()
    dsmock.controlWordCache.autonomous = 0
    assert not dsmock.isAutonomous()


def test_isTest(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.test = 1
    assert dsmock.isTest()
    dsmock.controlWordCache.test = 0
    assert not dsmock.isTest()


@pytest.mark.parametrize(
    "auto,test,oper", [(0, 0, True), (0, 1, False), (1, 0, False), (1, 1, False)]
)
def test_isOperatorControl(auto, test, oper, dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.autonomous = auto
    dsmock.controlWordCache.test = test
    assert dsmock.isOperatorControl() == oper


@pytest.mark.parametrize(
    "alliance", ["Red1", "Red2", "Red3", "Blue1", "Blue2", "Blue3", -1]
)
def test_getAlliance(alliance, dsmock, halmock):
    if alliance != -1:
        result = getattr(dsmock.Alliance, alliance[:-1])
        alliance = getattr(halmock.AllianceStationID, "k" + alliance)
    else:
        result = dsmock.Alliance.Invalid
    halmock.getAllianceStation.return_value = alliance
    assert dsmock.getAlliance() == result


@pytest.mark.parametrize(
    "alliance", ["Red1", "Red2", "Red3", "Blue1", "Blue2", "Blue3", -1]
)
def test_getLocation(alliance, dsmock, halmock):
    if alliance != -1:
        result = int(alliance[-1])
        alliance = getattr(halmock.AllianceStationID, "k" + alliance)
    else:
        result = 0
    halmock.getAllianceStation.return_value = alliance
    assert dsmock.getLocation() == result


def test_isFMSAttached_mock(dsmock, halmock):
    halmock.getFPGATime.return_value = 1000
    dsmock.controlWordCache.fmsAttached = 1
    assert dsmock.isFMSAttached()
    dsmock.controlWordCache.fmsAttached = 0
    assert not dsmock.isFMSAttached()


def test_isFMSAttached(ds, hal_data, sim_hooks):
    hal_data["control"]["fmsAttached"] = True
    sim_hooks.delaySeconds(0.1)
    assert ds.isFMSAttached()

    hal_data["control"]["fmsAttached"] = False
    assert ds.isFMSAttached()
    sim_hooks.delaySeconds(0.025)
    assert ds.isFMSAttached()
    sim_hooks.delaySeconds(0.03)
    assert not ds.isFMSAttached()


def test_getMatchTime(dsmock, halmock):
    assert dsmock.getMatchTime() == halmock.getMatchTime.return_value


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


def test_event_data(ds, hal_data):
    hal_data["event"]["name"] = "my-event"
    ds._getData()
    assert ds.getEventName() == "my-event"


def test_game_data(ds, hal_data):
    hal_data["event"]["game_specific_message"] = "LRL"
    ds._getData()
    assert ds.getGameSpecificMessage() == "LRL"


# HAL-only tests


def test_joystick_name(hal, hal_data):
    hal_data["joysticks"][0]["name"] = "joy0"
    hal_data["joysticks"][1]["name"] = "joy1"

    assert hal.getJoystickName(0) == "joy0"
    assert hal.getJoystickName(1) == "joy1"
