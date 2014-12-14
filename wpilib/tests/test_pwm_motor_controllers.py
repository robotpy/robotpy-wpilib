#
# Test the various types of PWM motor controllers in very simple ways
#

import pytest


@pytest.mark.parametrize('clsname, ',
                         ['Jaguar', 'Talon', 'TalonSRX', 'Victor', 'VictorSP'])
def test_controller(wpilib, hal_data, hal_impl_helpers, clsname):
    
    # create object/helper function
    obj = getattr(wpilib, clsname)(2)
    helper_fn = getattr(hal_impl_helpers, 'reverse%sPWM' % clsname)
    
    # validate reporting is correct
    assert hal_data['pwm'][2]['type'] == clsname.lower()
    
    # Assert starts with zero
    assert obj.get() == 0
    
    # call set
    obj.set(1)
    
    # validate that get returns the correct value
    assert obj.get() == 1
    
    # validate that the helper returns the correct value
    assert helper_fn(hal_data['pwm'][2]['value']) == 1
    
    # pidWrite
    obj.pidWrite(-1)
    
    assert obj.get() == -1
    assert helper_fn(hal_data['pwm'][2]['value']) == -1
    