import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def hal(request):
    return MagicMock(name='mock_hal')

@pytest.fixture(scope="function")
def frccan(request):
    return MagicMock(name='mock_frccan')

@pytest.fixture(scope="function")
def wpilib(request, hal, frccan):
    # need to monkey patch sys.modules so wpilib can load these
    m = patch.dict('sys.modules', {'frccan': frccan, 'hal': hal})
    m.start()
    request.addfinalizer(m.stop)
    import wpilib
    return wpilib
