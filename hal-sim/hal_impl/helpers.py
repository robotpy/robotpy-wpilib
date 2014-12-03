
from . import data
from .data import hal_data
from . import functions as fns
    
def notify_new_ds_data():
    '''Called when driver station data is modified'''
    
    if data.hal_newdata_sem is not None:
        fns.giveMultiWait(data.hal_newdata_sem)


def set_autonomous(enabled):
    '''Only designed to be called on transition'''
    
    hal_data['control'].update({
        'autonomous': True,
        'test': False,
        'enabled': enabled,
        'ds_attached': True
    })
    
    if enabled:
        hal_data['match_start'] = fns.hooks.getFPGATime()
    else:
        hal_data['match_start'] = None
    
    notify_new_ds_data()
    

def set_test_mode(enabled):
    '''Only designed to be called on transition'''
    
    hal_data['control'].update({
        'autonomous': True,
        'test': False,
        'enabled': enabled,
        'ds_attached': True
    })
    
    hal_data['match_start'] = None
    notify_new_ds_data()
    

def set_teleop_mode(enabled):
    '''Only designed to be called on transition'''
    
    hal_data['control'].update({
        'autonomous': False,
        'test': False,
        'enabled': enabled,
        'ds_attached': True
    })
    
    if enabled:
        hal_data['match_start'] = fns.hooks.getFPGATime() - 15000000
    else:
        hal_data['match_start'] = None
    
    notify_new_ds_data()


def set_disabled():
    '''Only designed to be called on transition'''
    
    hal_data['control'].update({
        'autonomous': False,
        'test': False,
        'enabled': False,
        'ds_attached': True
    })
    
    hal_data['match_start'] = None
    
    notify_new_ds_data()
        
    
    