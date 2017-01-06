
import pytest

def test_smartdashboard_basic(networktables, wpilib):
    
    ntsd = networktables.NetworkTables.getTable("SmartDashboard")
    
    sd = wpilib.SmartDashboard
    
    ntsd.putBoolean('bool', True)
    assert sd.getBoolean('bool') == True
    
    sd.putNumber('number', 1)
    assert ntsd.getNumber('number') == 1
    
    with pytest.raises(KeyError):
        sd.getString("string")
        
    ntsd.putString("string", "s")
    assert sd.getString("string") == "s"
    
    