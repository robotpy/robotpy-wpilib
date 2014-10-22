import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def hal(request):
    """Magic-mock for hal module."""
    hal = MagicMock(name='mock_hal')
    hal.kHALAllianceStationID_red1 = 0
    hal.kHALAllianceStationID_red2 = 1
    hal.kHALAllianceStationID_red3 = 2
    hal.kHALAllianceStationID_blue1 = 3
    hal.kHALAllianceStationID_blue2 = 4
    hal.kHALAllianceStationID_blue3 = 5
    hal.kMaxJoystickAxes = 12
    hal.kMaxJoystickPOVs = 12
    return hal

@pytest.fixture(scope="function")
def frccan(request):
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
def wpilib(request, hal, frccan):
    """Monkeypatches sys.modules hal and frccan and loads wpilib."""
    # need to monkey patch sys.modules so wpilib can load these
    m = patch.dict('sys.modules', {'frccan': frccan, 'hal': hal})
    m.start()
    request.addfinalizer(m.stop)
    import wpilib
    return wpilib
