import pytest
from unittest.mock import MagicMock

@pytest.fixture(scope='function')
def data(hal_data):
    return hal_data['compressor']

@pytest.fixture(scope='function')
def compressor(wpilib):
    return wpilib.Compressor()


def test_compressor_operation(compressor, data):
    
    compressor.start()
    assert compressor.getClosedLoopControl() == True
    
    compressor.stop()
    assert compressor.getClosedLoopControl() == False

def test_compressor_switch(compressor, data):

    data['pressure_switch'] = True
    assert compressor.getPressureSwitchValue() == True
    
def test_compressor_current(compressor, data):
    data['current'] = 42
    assert compressor.getCompressorCurrent() == 42
    
def test_compressor_sd(compressor):
    
    assert compressor.getSmartDashboardType() == 'Compressor'
    
    compressor.getTable = MagicMock()
    compressor.updateTable()