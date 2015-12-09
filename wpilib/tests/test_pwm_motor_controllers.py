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
    for i in [-1, -.9, -.7, -.3, 0, .3, .7, .9, 1]:
        obj.set(i)
        
        # validate that get returns the correct value
        assert abs(obj.get() - i) < 0.01
        
        obj.pidWrite(i)
        assert abs(obj.get() - i) < 0.01
        
        # validate that the helpers return the correct value and correct value stored in 'value'
        # .. to about 0.01
        assert abs(hal_impl_pwm_helpers.reverseByType(clsname ,hal_data['pwm'][2]['raw_value']) - i) < 0.01
        assert abs(hal_impl_pwm_helpers.reverseByType(2) - i) < 0.01
        assert abs(hal_data['pwm'][2]['value'] - i) < 0.01
    