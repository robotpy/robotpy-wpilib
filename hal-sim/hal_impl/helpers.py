'''
    Various helper functions useful for interacting with the HAL data
'''

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
        'autonomous': False,
        'test': True,
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
        
    
#
# Various functions that allow us to reverse the HW values used by HAL, as
# dealing directly with HW values is annoying
#

def reverseJaguarPWM(value):
    ''' :returns: value between -1 and 1'''
    
    max_pos_pwm = 1809
    min_pos_pwm = 1006
    pos_scale = 803
    max_neg_pwm = 1004
    min_neg_pwm = 196
    neg_scale = 808
    
    return rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale)

def reverseTalonPWM(value):
    ''' :returns: value between -1 and 1'''
    
    max_pos_pwm = 1536
    min_pos_pwm = 1012
    pos_scale = 524
    max_neg_pwm = 1010
    min_neg_pwm = 488
    neg_scale = 522
    
    return rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale)

def reverseTalonSRXPWM(value):
    ''' :returns: value between -1 and 1'''
    
    max_pos_pwm = 1503
    min_pos_pwm = 1000
    pos_scale = 503
    max_neg_pwm = 998
    min_neg_pwm = 496
    neg_scale = 502
    
    return rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale)

def reverseVictorPWM(value):
    ''' :returns: value between -1 and 1'''
    
    max_pos_pwm = 1526
    min_pos_pwm = 1006
    pos_scale = 520
    max_neg_pwm = 1004
    min_neg_pwm = 525
    neg_scale = 479
    
    return rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale)

def reverseVictorSPPWM(value):
    ''' :returns: value between -1 and 1'''
    
    max_pos_pwm = 1503
    min_pos_pwm = 1000
    pos_scale = 503
    max_neg_pwm = 998
    min_neg_pwm = 496
    neg_scale = 502
    
    return rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale)

def rev_pwm(value, max_pos_pwm, min_pos_pwm, pos_scale, max_neg_pwm, min_neg_pwm, neg_scale):
    # basically the PWM.getSpeed function
    if value > max_pos_pwm:
        return 1.0
    elif value < min_neg_pwm:
        return -1.0
    elif value > min_pos_pwm:
        return float(value - min_pos_pwm) / pos_scale
    elif value < max_neg_pwm:
        return float(value - max_neg_pwm) / neg_scale
    else:
        return 0.0

