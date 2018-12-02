import pytest
from networktables import NetworkTables
from unittest.mock import MagicMock


@pytest.fixture(scope="function")
def compressor_data(hal_data):
    return hal_data["compressor"]


@pytest.fixture(scope="function")
def compressor(wpilib):
    return wpilib.Compressor()


@pytest.fixture(scope="function")
def compressor_table(networktables):
    return networktables.NetworkTables.getTable("dacompressor")


def test_compressor_operation(compressor):

    compressor.start()
    assert compressor.getClosedLoopControl() == True

    compressor.stop()
    assert compressor.getClosedLoopControl() == False


@pytest.mark.parametrize("on_state,", [True, False])
def test_compressor_enabled(compressor, compressor_data, on_state):
    compressor_data["on"] = on_state
    assert compressor.enabled() == on_state


@pytest.mark.parametrize("switch_state,", [True, False])
def test_compressor_switch(compressor, compressor_data, switch_state):
    compressor_data["pressure_switch"] = switch_state
    assert compressor.getPressureSwitchValue() == switch_state


def test_compressor_current(compressor, compressor_data):
    compressor_data["current"] = 42
    assert compressor.getCompressorCurrent() == 42


@pytest.mark.parametrize("input,", [True, False])
def test_compressor_closedloopcontrol(compressor, compressor_data, input):
    compressor.setClosedLoopControl(input)
    assert compressor_data["closed_loop_enabled"] == input
    assert compressor.getClosedLoopControl() == input


def test_compressor_currenttoohighfault(compressor, compressor_data):
    # hal??
    assert compressor.getCompressorCurrentTooHighFault() == False


def test_compressor_currenttoohighstickyfault(compressor, compressor_data):
    # hal??
    assert compressor.getCompressorCurrentTooHighStickyFault() == False


def test_compressor_shortedstickyfault(compressor, compressor_data):
    # hal??
    assert compressor.getCompressorShortedStickyFault() == False


def test_compressor_shortedfault(compressor, compressor_data):
    # hal??
    assert compressor.getCompressorShortedFault() == False


def test_compressor_notconnectedfault(compressor, compressor_data):
    # hal??
    assert compressor.getCompressorNotConnectedFault() == False


def test_compressor_clearallpcmstickyfaults(compressor, compressor_data):
    # hal??
    compressor.clearAllPCMStickyFaults()


def test_compressor_initSendable_update(compressor, sendablebuilder, compressor_data):
    compressor_data["pressure_switch"] = True
    compressor_data["on"] = True
    compressor.initSendable(sendablebuilder)

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getString(".type", "") == "Compressor"
    assert sendablebuilder.getTable().getBoolean("Enabled", False) == True
    assert compressor.getPressureSwitchValue() == True
    assert sendablebuilder.getTable().getBoolean("Pressure switch", False) == True


def test_compressor_initSendable_setter(compressor, sendablebuilder, compressor_data):
    compressor_data["pressure_switch"] = True
    compressor.initSendable(sendablebuilder)

    sendablebuilder.updateTable()

    [enabled_prop, pressure_prop] = sendablebuilder.properties
    assert enabled_prop.key == "Enabled"
    assert pressure_prop.key == "Pressure switch"
    assert pressure_prop.setter is None

    assert compressor.getClosedLoopControl() == False
    enabled_prop.setter(True)
    assert compressor.getClosedLoopControl() == True


def test_enabledchanged_true(compressor):
    compressor.start = MagicMock()

    compressor.enabledChanged(True)
    assert compressor.start.called


def test_enabledchanged_false(compressor):
    compressor.stop = MagicMock()

    compressor.enabledChanged(False)
    assert compressor.stop.called
