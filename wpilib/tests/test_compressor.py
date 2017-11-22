import pytest
from networktables import NetworkTables
from unittest.mock import MagicMock


@pytest.fixture(scope='function')
def compressor_data(hal_data):
    return hal_data['compressor']


@pytest.fixture(scope='function')
def compressor(wpilib):
    return wpilib.Compressor()


@pytest.fixture(scope='function')
def compressor_table(networktables):
    return networktables.NetworkTables.getTable("dacompressor")


def test_compressor_operation(compressor):
    
    compressor.start()
    assert compressor.getClosedLoopControl() == True
    
    compressor.stop()
    assert compressor.getClosedLoopControl() == False


@pytest.mark.parametrize("on_state,", [True, False])
def test_compressor_enabled(compressor, compressor_data, on_state):
    compressor_data['on'] = on_state
    assert compressor.enabled() == on_state


@pytest.mark.parametrize("switch_state,", [True, False])
def test_compressor_switch(compressor, compressor_data, switch_state):
    compressor_data['pressure_switch'] = switch_state
    assert compressor.getPressureSwitchValue() == switch_state
    

def test_compressor_current(compressor, compressor_data):
    compressor_data['current'] = 42
    assert compressor.getCompressorCurrent() == 42
    

@pytest.mark.parametrize("input,", [True, False])
def test_compressor_closedloopcontrol(compressor, compressor_data, input):
    compressor.setClosedLoopControl(input)
    assert compressor_data['closed_loop_enabled'] == input
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


def test_compressor_sd(compressor):
    
    assert compressor.getSmartDashboardType() == 'Compressor'
    
    compressor.getTable = MagicMock()
    compressor.updateTable()


def test_compressor_inittable_nulltable(compressor, compressor_data):
    compressor_data['pressure_switch'] = True
    compressor_data['on'] = True
    compressor.initTable(None)

    assert compressor.enabledEntry is None


def test_compressor_inittable(compressor, compressor_table, compressor_data):
    compressor_data['pressure_switch'] = True
    compressor_data['on'] = True
    compressor.initTable(compressor_table)

    assert compressor_table.getBoolean("Enabled", False) == True 
    assert compressor_table.getBoolean("Pressure Switch", False) == True 


def test_compressor_updateTable_nullentry(compressor, compressor_data):
    compressor.getPressureSwitchValue = MagicMock()
    compressor.enabled = MagicMock()
    compressor.updateTable()

    compressor.getPressureSwitchValue.assert_not_called()
    compressor.enabled.assert_not_called()


def test_startlivewindowmode(compressor, compressor_data):
    compressor.enabledEntry = MagicMock()

    assert compressor.enabledListener is None
    compressor.startLiveWindowMode()

    compressor.enabledEntry.addListener.assert_called_with(compressor.enabledChanged, 
                NetworkTables.NotifyFlags.IMMEDIATE |
                NetworkTables.NotifyFlags.NEW |
                NetworkTables.NotifyFlags.UPDATE)
    assert compressor.enabledListener is not None


def test_startlivewindowmode_null_entry(compressor):
    compressor.enabledEntry = None

    assert compressor.enabledListener is None
    compressor.startLiveWindowMode()

    assert compressor.enabledListener is None


def test_enabledchanged_true(compressor):
    compressor.start = MagicMock()

    compressor.enabledChanged(None, None, True, None)
    assert compressor.start.called


def test_enabledchanged_false(compressor):
    compressor.stop = MagicMock()

    compressor.enabledChanged(None, None, False, None)
    assert compressor.stop.called


def test_stoplivewindowmode(compressor):
    compressor.enabledEntry = MagicMock()

    compressor.startLiveWindowMode()

    assert compressor.enabledListener is not None

    compressor.stopLiveWindowMode()

    assert compressor.enabledListener is None


def test_stoplivewindowmode_null_entry(compressor):
    compressor.enabledEntry = None

    compressor.startLiveWindowMode()

    assert compressor.enabledListener is None

    compressor.stopLiveWindowMode()

    assert compressor.enabledListener is None
