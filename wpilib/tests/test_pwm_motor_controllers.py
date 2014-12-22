#
# Test the various types of PWM motor controllers in very simple ways
#

import pytest


@pytest.mark.parametrize('clsname, ',
                         ['Jaguar', 'Talon', 'TalonSRX', 'Victor', 'VictorSP'])
def test_controller(wpilib, hal_data, hal_impl_pwm_helpers, clsname):
    
    # create object/helper function
    obj = getattr(wpilib, clsname)(2)
    
    # validate reporting is correct
    assert hal_data['pwm'][2]['type'] == clsname.lower()
    
    # Assert starts with zero
    assert obj.get() == 0
    
    # call set
    obj.set(1)
    
    # validate that get returns the correct value
    assert obj.get() == 1
    
    # validate that the helpers return the correct value and correct value stored in 'value'
    assert hal_impl_pwm_helpers.reverseByType(clsname ,hal_data['pwm'][2]['raw_value']) == 1
    assert hal_impl_pwm_helpers.reverseByType(2) == 1
    assert hal_data['pwm'][2]['value'] == 1
    
    # pidWrite
    obj.pidWrite(-1)
    
    assert obj.get() == -1
    assert hal_impl_pwm_helpers.reverseByType(clsname ,hal_data['pwm'][2]['raw_value']) == -1
    assert hal_impl_pwm_helpers.reverseByType(2) == -1
    assert hal_data['pwm'][2]['value'] == -1