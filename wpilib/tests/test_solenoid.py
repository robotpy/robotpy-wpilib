
import pytest
from unittest.mock import MagicMock
from ntcore.entry_notifier import _EntryNotification

def test_doublesolenoid_set(wpilib, hal, hal_data):
    
    ds = wpilib.DoubleSolenoid(0, 1)
    
    with pytest.raises(hal.exceptions.HALError):
        wpilib.Solenoid(1)
    
    assert ds.get() == ds.Value.kOff
    
    ds.set(ds.Value.kForward)
    assert ds.get() == ds.Value.kForward
    assert hal_data['solenoid'][0]['value'] == True
    assert hal_data['solenoid'][1]['value'] == False
    
    ds.set(ds.Value.kOff)
    assert ds.get() == ds.Value.kOff
    assert hal_data['solenoid'][0]['value'] == False
    assert hal_data['solenoid'][1]['value'] == False
    
    ds.set(ds.Value.kReverse)
    assert ds.get() == ds.Value.kReverse
    assert hal_data['solenoid'][0]['value'] == False
    assert hal_data['solenoid'][1]['value'] == True
    
    ds.free()
    
    ds = wpilib.DoubleSolenoid(0, 1)
    
    

def test_solenoid(wpilib, hal, hal_data):

    for i in range(wpilib.SensorBase.kSolenoidChannels):
        
        # ensure that it can be freed and allocated again
        for _ in range(2):        
            s = wpilib.Solenoid(i)
            
            with pytest.raises(hal.exceptions.HALError):
                wpilib.Solenoid(i)
            
            assert hal_data['solenoid'][i]['initialized']
            
            for v in [True, False, True, True, False]:
                s.set(v)
                assert hal_data['solenoid'][i]['value'] == v
                
                nv = not v
                hal_data['solenoid'][i]['value'] = nv 
                assert s.get() == nv
                
            s.free()
            
            with pytest.raises(ValueError):
                s.set(True)


def test_multiple_solenoids(wpilib, hal_data):
    
    assert not hal_data['solenoid'][4]['initialized']
    assert not hal_data['solenoid'][2]['initialized']
    
    s1 = wpilib.Solenoid(4)
    assert hal_data['solenoid'][4]['initialized']
    
    s2 = wpilib.Solenoid(2)
    assert hal_data['solenoid'][2]['initialized']
    
    for i, s in [(4, s1), (2, s2)]:
        for v in [True, False, True, True, False]:
            s.set(v)
            assert hal_data['solenoid'][i]['value'] == v
            
            nv = not v
            hal_data['solenoid'][i]['value'] = nv
            assert s.get() == nv
    

@pytest.mark.parametrize("value,expected",
    [(True, True), (False, False)])
def test_solenoid_valueChanged(value, expected, wpilib, hal_data):
    s1 = wpilib.Solenoid(4)
    s1.set = MagicMock()
    s1.valueChanged(_EntryNotification(name='Value', value=value, flags=1, local_id=1))

    s1.set.assert_called_once_with(expected)

def test_solenoidbase_getAll(wpilib, hal_data):
    
    solenoid = wpilib.SolenoidBase(0)
    
    for s in hal_data['solenoid']:
        s['value'] = False
        
    assert solenoid.getAll() == 0
    
    for s in hal_data['solenoid']:
        s['value'] = True
        
    assert solenoid.getAll() == 0xFF
    assert wpilib.SolenoidBase.getAll(0) == 0xFF
    
    hal_data['solenoid'][0]['value'] = False
    
    assert solenoid.getAll() == 0xFE
    assert wpilib.SolenoidBase.getAll(0) == 0xFE

def test_pcm_mapping(wpilib, hal_data):
    assert hal_data['solenoid'] is hal_data['pcm'][0]

def test_multiple_pcm(wpilib, hal_data):
    
    s0_1 = wpilib.Solenoid(0, 1)
    s1_1 = wpilib.Solenoid(1, 1)
    
    hal_data['pcm'][0][1]['value'] = True
    hal_data['pcm'][1][1]['value'] = False
    assert s0_1.get() == True
    assert s1_1.get() == False
    
    hal_data['pcm'][0][1]['value'] = False
    hal_data['pcm'][1][1]['value'] = True
    assert s0_1.get() == False
    assert s1_1.get() == True

