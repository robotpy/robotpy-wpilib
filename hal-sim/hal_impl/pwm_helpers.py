from . import data
from .data import hal_data

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

def reverseByType(defining_val , value=None):
    ''' 
        Returns translated value type based on the type value of the pwm hal_data
        entry
        
        :param defining_val:  Either a string that defines the type of pwm this should be or
                              a number defining the instance we should be reversing
        :param value:         raw value to transform, not used if defining_val int defining an instance
        :returns:             value between -1 and 1
    '''
    if isinstance(defining_val, str):
        type = defining_val.lower()
        if value != None:
            trans_val = value
        else:
            raise ValueError("Must have a value to translate")
    
    else:
        type = hal_data['pwm'][defining_val]['type']
        trans_val = hal_data['pwm'][defining_val]['raw_value']
    
    if type == 'jaguar':
        return reverseJaguarPWM(trans_val)
    elif type == 'talon':
        return reverseTalonPWM(trans_val)
    elif type == 'talonsrx':
        return reverseTalonSRXPWM(trans_val)
    elif type == 'victor':
        return reverseVictorPWM(trans_val)
    elif type == 'victorsp':
        return reverseVictorSPPWM(trans_val)
    else:
        # hal may not have been reported to yet so just set this to zero
        if type != None:
            raise   TypeError('The type ' + str(type) + 'is not a useable motor controller type')
        
        return 0

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