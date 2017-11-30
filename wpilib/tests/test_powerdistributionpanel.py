import pytest


@pytest.fixture(scope="function")
def pdp(wpilib):
    return wpilib.PowerDistributionPanel()


@pytest.fixture(scope="function")
def pdp_table(networktables):
    return networktables.NetworkTables.getTable("pdplikethang")


@pytest.fixture(scope="function")
def pdp_data(hal_data):
    return hal_data['pdp']


def test_pdp_getVoltage(pdp, pdp_data):
    pdp_data['voltage'] = 3.14
    assert pdp.getVoltage() == 3.14


def test_pdp_getTemperature(pdp, pdp_data):
    pdp_data['temperature'] = 90
    assert pdp.getTemperature() == 90


def test_pdp_getCurrent(pdp, pdp_data):
    pdp_data['current'][3] = 15
    assert pdp.getCurrent(3) == 15


@pytest.mark.parametrize("value", [-1, 16])
def test_pdp_getCurrent_limits(value, pdp):
    with pytest.raises(IndexError):
        pdp.getCurrent(value)


def test_pdp_getTotalCurrent(pdp, pdp_data):
    pdp_data['total_current'] = 42
    assert pdp.getTotalCurrent() == 42

    
def test_pdp_getTotalPower(pdp, pdp_data):
    pdp_data['total_power'] = 42
    assert pdp.getTotalPower() == 42

    
def test_pdp_getTotalEnergy(pdp, pdp_data):
    pdp_data['total_energy'] = 42
    assert pdp.getTotalEnergy() == 42


def test_pdp_resetTotalEnergy(pdp, pdp_data):
    pdp_data['total_energy'] = 42
    pdp.resetTotalEnergy()
    assert pdp_data['total_energy'] == 0


def test_pdp_clearStickyFaults(pdp):
    pdp.clearStickyFaults()


def test_pdp_initTable_null(pdp):
    pdp.initTable(None)


def test_pdp_initTable_null(pdp, pdp_data, pdp_table):
    pdp_data['current'][0] = 15
    pdp_data['current'][15] = 25
    pdp_data['voltage'] = 3.14
    pdp_data['total_current'] = 42
    pdp.initTable(pdp_table)

    assert pdp_table.getNumber("Chan0", 0.0) == pytest.approx(15, 0.01)
    assert pdp_table.getNumber("Chan15", 0.0) == pytest.approx(25, 0.01)
    assert pdp_table.getNumber("Voltage", 0.0) == pytest.approx(3.14, 0.01)
    assert pdp_table.getNumber("TotalCurrent", 0.0) == pytest.approx(42, 0.01)


def test_pdp_livewindowmode(pdp, pdp_table):

    pdp.initTable(pdp_table)

    pdp.startLiveWindowMode()
    assert not hasattr(pdp, 'valueListener')
    assert not hasattr(pdp, 'voltageListener')
    assert not hasattr(pdp, 'totalCurrentListener')
    pdp.stopLiveWindowMode()

