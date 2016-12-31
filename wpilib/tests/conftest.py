
import sys
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(scope="function")
def _module_patch(request):
    '''This patch forces wpilib to reload each time we do this'''
    
    assert 'halmock' not in request.fixturenames, "Cannot use mock and real fixtures in same function!"
    
    assert 'wpilib' not in sys.modules, "Must use wpilib fixture, don't import wpilib directly"
    
    # .. this seems inefficient
    
    m = patch.dict('sys.modules', {})
    m.start()
    request.addfinalizer(m.stop)

@pytest.fixture(scope="function")
def hal(_module_patch):
    """Simulated hal module"""
    import hal
    return hal

@pytest.fixture(scope="function")
def hal_impl_mode_helpers(_module_patch):
    """Simulated hal module"""
    from hal_impl import mode_helpers
    return mode_helpers

@pytest.fixture(scope="function")
def hal_data(_module_patch):
    """Simulation data for HAL"""
    import hal_impl.functions
    import hal_impl.data
    hal_impl.functions.reset_hal()
    return hal_impl.data.hal_data

@pytest.fixture(scope="function")
def wpilib(_module_patch, hal, hal_data):
    """Actual wpilib implementation"""
    import wpilib
    return wpilib

    # Note: we don't use wpilib.Resource._reset here because the wpilib module
    # is freshly loaded each time a new test is ran

@pytest.fixture(scope="function")
def networktables():
    """Networktables instance"""
    import networktables
    networktables.NetworkTables.setTestMode()
    return networktables

#
# Mock fixtures for testing things that don't have to interact with 
# hardware, so it's better to use MagicMock to create those tests
#


@pytest.fixture(scope="function")
def halmock(request):
    """Magic-mock for hal module."""
    
    assert '_module_patch' not in request.fixturenames, "Cannot use mock and real fixtures in same function!"
    
    hal = MagicMock(name='mock_hal')
    hal.kHALAllianceStationID_red1 = 0
    hal.kHALAllianceStationID_red2 = 1
    hal.kHALAllianceStationID_red3 = 2
    hal.kHALAllianceStationID_blue1 = 3
    hal.kHALAllianceStationID_blue2 = 4
    hal.kHALAllianceStationID_blue3 = 5
    hal.AllianceStationID.kRed1 = 0
    hal.AllianceStationID.kRed2 = 1
    hal.AllianceStationID.kRed3 = 2
    hal.AllianceStationID.kBlue1 = 3
    hal.AllianceStationID.kBlue2 = 4
    hal.AllianceStationID.kBlue3 = 5
    hal.kMaxJoystickAxes = 12
    hal.kMaxJoystickPOVs = 12
    return hal

@pytest.fixture(scope="function")
def wpimock(request, halmock):
    """Monkeypatches sys.modules hal and loads wpilib."""
    
    assert '_module_patch' not in request.fixturenames, "Cannot use mock and real fixtures in same function!"
    
    # need to monkey patch sys.modules so wpilib can load these
    m = patch.dict('sys.modules', {'hal': halmock})
    m.start()
    request.addfinalizer(m.stop)
    import wpilib
    return wpilib




