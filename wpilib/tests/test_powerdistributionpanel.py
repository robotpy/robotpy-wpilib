import pytest

@pytest.fixture(scope="function")
def pdp(wpilib):
    return wpilib.PowerDistributionPanel()

def test_pdp_getVoltage(pdp, hal):
    rv = pdp.getVoltage()
    hal.getPDPVoltage.assert_called_once_with()
    assert rv == hal.getPDPVoltage.return_value

def test_pdp_getTemperature(pdp, hal):
    rv = pdp.getTemperature()
    hal.getPDPTemperature.assert_called_once_with()
    assert rv == hal.getPDPTemperature.return_value

def test_pdp_getCurrent(pdp, hal):
    rv = pdp.getCurrent(3)
    hal.getPDPChannelCurrent.assert_called_once_with(3)
    assert rv == hal.getPDPChannelCurrent.return_value

@pytest.mark.parametrize("value", [-1, 16])
def test_pdp_getCurrent_limits(value, pdp, hal):
    with pytest.raises(IndexError):
        rv = pdp.getCurrent(value)
    assert not hal.getPDPChannelCurrent.called

