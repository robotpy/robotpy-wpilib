import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def module_patch(request):
    '''This patch forces wpilib to reload each time we do this'''
    
    # .. this seems inefficient
    
    m = patch.dict('sys.modules', {})
    m.start()
    request.addfinalizer(m.stop)

@pytest.fixture(scope="function")
def hal(module_patch):
    import hal
    return hal

@pytest.fixture(scope="function")
def hal_data(module_patch):
    import hal_impl.data
    hal_impl.data.reset_hal_data()
    return hal_impl.data.hal_data

@pytest.fixture(scope="function")
def frccan(request):
    
    # Not sure how to deal with this yet
    assert False
    
    """Mock for frccan module."""
    frccan = MagicMock(name='mock_frccan')

    class CANError(RuntimeError):
        pass
    class CANMessageNotFound(CANError):
        pass

    frccan.CANError = CANError
    frccan.CANMessageNotFound = CANMessageNotFound

    # Flags in the upper bits of the messageID
    frccan.CAN_IS_FRAME_REMOTE = 0x80000000
    frccan.CAN_IS_FRAME_11BIT = 0x40000000

    return frccan

@pytest.fixture(scope="function")
def wpilib(module_patch, hal, hal_data):
    import wpilib
    return wpilib
    
