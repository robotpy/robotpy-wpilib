import pytest


@pytest.fixture(scope="function")
def data(hal_data):
    return hal_data["power"]


def test_getInputVoltage(wpilib, data):
    data["vin_voltage"] = 3.14
    assert wpilib.ControllerPower.getInputVoltage() == 3.14


def test_getInputCurrent(wpilib, data):
    data["vin_current"] = 3.14
    assert wpilib.ControllerPower.getInputCurrent() == 3.14


def test_getVoltage3V3(wpilib, data):
    data["user_voltage_3v3"] = 3.14
    assert wpilib.ControllerPower.getVoltage3V3() == 3.14


def test_getCurrent3V3(wpilib, data):
    data["user_current_3v3"] = 3.14
    assert wpilib.ControllerPower.getCurrent3V3() == 3.14


def test_getEnabled3V3(wpilib, data):
    data["user_active_3v3"] = True
    assert wpilib.ControllerPower.getEnabled3V3() == True


def test_getFaultCount3V3(wpilib, data):
    data["user_faults_3v3"] = 3
    assert wpilib.ControllerPower.getFaultCount3V3() == 3


def test_getVoltage5V(wpilib, data):
    data["user_voltage_5v"] = 3.14
    assert wpilib.ControllerPower.getVoltage5V() == 3.14


def test_getCurrent5V(wpilib, data):
    data["user_current_5v"] = 3.14
    assert wpilib.ControllerPower.getCurrent5V() == 3.14


def test_getEnabled5V(wpilib, data):
    data["user_active_5v"] = True
    assert wpilib.ControllerPower.getEnabled5V() == True


def test_getFaultCount5V(wpilib, data):
    data["user_faults_5v"] = 3
    assert wpilib.ControllerPower.getFaultCount5V() == 3


def test_getVoltage6V(wpilib, data):
    data["user_voltage_6v"] = 3.14
    assert wpilib.ControllerPower.getVoltage6V() == 3.14


def test_getCurrent6V(wpilib, data):
    data["user_current_6v"] = 3.14
    assert wpilib.ControllerPower.getCurrent6V() == 3.14


def test_getEnabled6V(wpilib, data):
    data["user_active_6v"] = True
    assert wpilib.ControllerPower.getEnabled6V() == True


def test_getFaultCount6V(wpilib, data):
    data["user_faults_6v"] = 3
    assert wpilib.ControllerPower.getFaultCount6V() == 3
