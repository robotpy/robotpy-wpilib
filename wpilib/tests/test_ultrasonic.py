

def test_ultrasonic_auto(wpilib, hal_data):
    
    u = wpilib.Ultrasonic(1, 2)
    
    # This used to fail
    u.setAutomaticMode(True)
    u.setAutomaticMode(False)
    u.setAutomaticMode(True)
    
    assert u.isEnabled() == True
    u.setEnabled(False)
    assert u.isEnabled() == False
    u.setEnabled(True)
    
    u.setAutomaticMode(False)
    
    
    u.ping()
    
    assert u.isRangeValid() == False
    hal_data['counter'][0]['count'] = 5
    assert u.isRangeValid() == True
    
    u.free()
    