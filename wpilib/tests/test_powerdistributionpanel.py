import pytest


@pytest.fixture(scope="function")
def pdp(wpilib):
    return wpilib.PowerDistributionPanel()


@pytest.fixture(scope="function")
def pdp_table(networktables):
    return networktables.NetworkTables.getTable("pdplikethang")


@pytest.fixture(scope="function")
def pdp_data(hal_data):
    return hal_data["pdp"][0]


def test_pdp_getVoltage(pdp, pdp_data):
    pdp_data["voltage"] = 3.14
    assert pdp.getVoltage() == 3.14


def test_pdp_getTemperature(pdp, pdp_data):
    pdp_data["temperature"] = 90
    assert pdp.getTemperature() == 90


def test_pdp_getCurrent(pdp, pdp_data):
    pdp_data["current"][3] = 15
    assert pdp.getCurrent(3) == 15


@pytest.mark.parametrize("value", [-1, 16])
def test_pdp_getCurrent_limits(value, pdp):
    with pytest.raises(IndexError):
        pdp.getCurrent(value)


def test_pdp_getTotalCurrent(pdp, pdp_data):
    pdp_data["total_current"] = 42
    assert pdp.getTotalCurrent() == 42


def test_pdp_getTotalPower(pdp, pdp_data):
    pdp_data["total_power"] = 42
    assert pdp.getTotalPower() == 42


def test_pdp_getTotalEnergy(pdp, pdp_data):
    pdp_data["total_energy"] = 42
    assert pdp.getTotalEnergy() == 42


def test_pdp_resetTotalEnergy(pdp, pdp_data):
    pdp_data["total_energy"] = 42
    pdp.resetTotalEnergy()
    assert pdp_data["total_energy"] == 0


def test_pdp_clearStickyFaults(pdp):
    pdp.clearStickyFaults()


def test_pdp_initSendable(pdp, pdp_data, sendablebuilder):
    pdp_data["current"][0] = 15
    pdp_data["current"][15] = 1
    pdp_data["voltage"] = 11.50
    pdp_data["total_current"] = 46
    pdp.initSendable(sendablebuilder)
    assert sendablebuilder.properties[0].key == "Chan0"
    assert sendablebuilder.properties[1].key == "Chan1"
    assert sendablebuilder.properties[15].key == "Chan15"
    assert sendablebuilder.properties[16].key == "Voltage"
    assert sendablebuilder.properties[17].key == "TotalCurrent"

    prop = sendablebuilder.properties[0]
    assert prop.setter is None
    prop = sendablebuilder.properties[16]
    assert prop.setter is None
    prop = sendablebuilder.properties[17]
    assert prop.setter is None

    sendablebuilder.updateTable()

    assert sendablebuilder.getTable().getNumber("Chan0", 0.0) == 15
    assert sendablebuilder.getTable().getNumber("Voltage", 0.0) == pytest.approx(11.50)
    assert sendablebuilder.getTable().getNumber("TotalCurrent", 0.0) == 46
