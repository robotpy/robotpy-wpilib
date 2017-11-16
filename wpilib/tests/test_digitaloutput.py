import pytest

def test_init(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)
    assert hal_data['dio'][2]['initialized']
    assert not hal_data['dio'][2]['is_input']

def test_get(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)
    hal_data['dio'][2]['value'] = True
    assert di.get()
    
def test_set(wpilib, hal_data):
    di = wpilib.DigitalOutput(2)
    
    di.set(True)
    assert hal_data['dio'][2]['value'] == True
    
    di.set(False)
    assert hal_data['dio'][2]['value'] == False

def test_is_analog_trigger(wpilib):
    di = wpilib.DigitalOutput(2)
    assert not di.isAnalogTrigger()
