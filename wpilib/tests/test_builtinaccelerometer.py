import pytest
from unittest.mock import MagicMock, call

@pytest.fixture(scope='function')
def acc(wpilib):
    return wpilib.BuiltInAccelerometer()

@pytest.fixture(scope='function')
def acc_data(hal_data):
    return hal_data['accelerometer']



@pytest.mark.parametrize('range', ['k2G', 'k4G', 'k8G'])
def test_bacc_setRange(wpilib, range, acc, acc_data):
    range = getattr(wpilib.BuiltInAccelerometer.Range, range)
    acc.setRange(range)
    assert acc_data['range'] == range
    
def test_bacc_setRange_invalid(wpilib, acc_data):
    with pytest.raises(ValueError):
        _ = wpilib.BuiltInAccelerometer(range=wpilib.BuiltInAccelerometer.Range.k16G)
        
    assert acc_data['active'] == False


def test_bacc_getX(acc, acc_data):
    acc_data['x'] = 3.14
    assert acc.getX() == 3.14

def test_bacc_getY(acc, acc_data):
    acc_data['y'] = 3.14
    assert acc.getY() == 3.14

def test_bacc_getZ(acc, acc_data):
    acc_data['z'] = 3.14
    assert acc.getZ() == 3.14

def test_bacc_getSmartDashboardType(acc):
    assert acc.getSmartDashboardType() == "Accelerometer"
    
@pytest.mark.parametrize('table', [True, False])
def test_bacc_updateTable(acc, acc_data, table):
    acc.getTable = MagicMock()
    if not table:
        acc.getTable.return_value = None
        acc.getX = MagicMock()
        acc.updateTable()
        assert not acc.getX.called
    else:
        acc_data['x'] = 1
        acc_data['y'] = 2
        acc_data['z'] = 3
        acc.updateTable()
        acc.getTable.return_value.putNumber.assert_has_calls([call('X', 1),
                                                              call('Y', 2),
                                                              call('Z', 3)])

        
        
