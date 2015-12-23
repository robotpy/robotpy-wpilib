from . import data
from .data import hal_data

#
# Various functions that allow us to reverse the HW values used by HAL, as
# dealing directly with HW values is annoying
#

rev_types = {
    'jaguar':   (1809, 1006, 803, 1004, 196, 808),
    'sd540':    (1548, 1000, 548, 998, 439, 559),
    'spark':    (1502, 1000, 502, 998, 498, 500),
    'talon':    (1536, 1012, 524, 1010, 488, 522),
    'talonsrx': (1503, 1000, 503, 998, 496, 502),
    'victor':   (1526, 1006, 520, 1004, 525, 479),
    'victorsp': (1503, 1000, 503, 998, 496, 502),
}

# Calculate these numbers via:
#
# f = wpilib.Spark(1)
# print(', '.join(str(i) for i in [f.getMaxPositivePwm(), f.getMinPositivePwm(),
#               f.getPositiveScaleFactor(), f.getMaxNegativePwm(),
#               f.getMinNegativePwm(), f.getNegativeScaleFactor()]))
#

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
    
    vals = rev_types.get(type)
    if vals:
        return rev_pwm(trans_val, *vals)
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