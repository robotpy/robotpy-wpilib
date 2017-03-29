
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
    
def test_smartdashboard_chooser(networktables, wpilib):
    
    ntsd = networktables.NetworkTables.getTable("SmartDashboard")
    
    o1 = object()
    o2 = object()
    o3 = object()
    
    chooser = wpilib.SendableChooser()
    chooser.addObject('o1', o1)
    chooser.addObject('o2', o2)
    chooser.addDefault('o3', o3)
    
    
    
    # Default should work
    assert chooser.getSelected() == o3
    
    wpilib.SmartDashboard.putData('Autonomous Mode', chooser)
    
    assert chooser.table is not None
    
    # Default should still work
    assert chooser.getSelected() == o3
    
    # switch it up
    ct = ntsd.getSubTable('Autonomous Mode')
    ct.putString(chooser.SELECTED, "o1")
    
    # New choice should now be returned
    assert chooser.getSelected() == o1
    