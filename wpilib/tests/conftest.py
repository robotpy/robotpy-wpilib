import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def hal(request):
    """Magic-mock for hal module."""
    return MagicMock(name='mock_hal')

@pytest.fixture(scope="function")
def frccan(request):
    """Magic-mock for frccan module."""
    return MagicMock(name='mock_frccan')

@pytest.fixture(scope="function")
def wpilib(request, hal, frccan):
    """Monkeypatches sys.modules hal and frccan and loads wpilib."""
    # need to monkey patch sys.modules so wpilib can load these
    m = patch.dict('sys.modules', {'frccan': frccan, 'hal': hal})
    m.start()
    request.addfinalizer(m.stop)
    import wpilib
    return wpilib
