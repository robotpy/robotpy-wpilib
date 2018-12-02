import pytest


@pytest.fixture(scope="function")
def data(hal_data):
    return hal_data["power"]


@pytest.fixture(scope="function")
def rc(wpilib):
    return wpilib.RobotController


def test_rc_getFPGAVersion(rc):
    assert rc.getFPGAVersion() == 2018


def test_rc_getFPGARevision(rc):
    assert rc.getFPGARevision() == 0


def test_rc_getFPGATime(rc, hal_data, monkeypatch):
    import time

    monkeypatch.setattr(time, "monotonic", lambda: 3.14)
    hal_data["time"]["program_start"] = 1
    assert rc.getFPGATime() == 2.14 * 1000000


def test_rc_getUserButton(rc, hal_data):
    hal_data["fpga_button"] = True
    assert rc.getUserButton() == True


def test_getInputVoltage(wpilib, data):
    data["vin_voltage"] = 3.14
    assert wpilib.RobotController.getInputVoltage() == 3.14


def test_getInputCurrent(wpilib, data):
    data["vin_current"] = 3.14
    assert wpilib.RobotController.getInputCurrent() == 3.14


def test_getVoltage3V3(wpilib, data):
    data["user_voltage_3v3"] = 3.14
    assert wpilib.RobotController.getVoltage3V3() == 3.14


def test_getCurrent3V3(wpilib, data):
    data["user_current_3v3"] = 3.14
    assert wpilib.RobotController.getCurrent3V3() == 3.14


def test_getEnabled3V3(wpilib, data):
    data["user_active_3v3"] = True
    assert wpilib.RobotController.getEnabled3V3() == True


def test_getFaultCount3V3(wpilib, data):
    data["user_faults_3v3"] = 3
    assert wpilib.RobotController.getFaultCount3V3() == 3


def test_getVoltage5V(wpilib, data):
    data["user_voltage_5v"] = 3.14
    assert wpilib.RobotController.getVoltage5V() == 3.14


def test_getCurrent5V(wpilib, data):
    data["user_current_5v"] = 3.14
    assert wpilib.RobotController.getCurrent5V() == 3.14


def test_getEnabled5V(wpilib, data):
    data["user_active_5v"] = True
    assert wpilib.RobotController.getEnabled5V() == True


def test_getFaultCount5V(wpilib, data):
    data["user_faults_5v"] = 3
    assert wpilib.RobotController.getFaultCount5V() == 3


def test_getVoltage6V(wpilib, data):
    data["user_voltage_6v"] = 3.14
    assert wpilib.RobotController.getVoltage6V() == 3.14


def test_getCurrent6V(wpilib, data):
    data["user_current_6v"] = 3.14
    assert wpilib.RobotController.getCurrent6V() == 3.14


def test_getEnabled6V(wpilib, data):
    data["user_active_6v"] = True
    assert wpilib.RobotController.getEnabled6V() == True


def test_getFaultCount6V(wpilib, data):
    data["user_faults_6v"] = 3
    assert wpilib.RobotController.getFaultCount6V() == 3
