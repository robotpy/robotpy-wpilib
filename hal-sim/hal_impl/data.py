#
# All data that passes through the HAL comes to/from here
#

from hal import constants
import sys

import logging
logger = logging.getLogger('hal.data')

#: Dictionary of all robot data
hal_data = {
    # don't fill this out, fill out the version in reset_hal_data
}

#: A multiwait object. Use hal.giveMultiWait() to set this when
#: driver station related data has been updated
hal_newdata_sem = None



class NotifyDict(dict):
    '''
        Allows us to listen to changes in the dictionary -- 
        note that we don't wrap everything, because for our
        purposes we don't care about the rest
        
        We only use these for some keys in the hal_data dict, 
        as not all keys are useful to listen to
    '''
    __slots__ = ['cbs']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cbs = {}
        
    def register(self, k, cb, notify=False):
        '''
            register a function to be called when an item is set 
            with in this dictionary. We raise a key error if the 
            key passed is not a key that the dictionary contains.

            :param k:        Key to be registered for call back. The key must be a
                             valid key with in the dictionary
            :param cb:       Function to be called if k is set. This function needs 
                             to take at least 2 parameters
            :param notify:   Calls the function cb after registering k                
        '''
        if k not in self:
            raise KeyError("Cannot register for non-existant key '%s'" % k)
        self.cbs.setdefault(k, []).append(cb)
        if notify:
            cb(k, self[k])
        
    def __setitem__(self, k, v):
        '''
           Overrides __setitem__. If k has any callback functions defined they are
           called from here
           
           :param k: key to be set
           :param v: value to be set
        '''     
        super().__setitem__(k, v)
        
        # Call the callbacks
        for cb in self.cbs.get(k, []):
            try:
                cb(k, v)
            except:
                logger.exception("BAD INTERNAL ERROR")
        

def _reset_hal_data(hooks):
    '''
        Intended to be used by the test runner or simulator. Don't call this
        directly, instead call hal_impl.reset_hal()
        
        Subject to change until the simulator is fully developed, as the
        usefulness of some of this isn't immediately clear yet.
        
        Generally, non-hal components should only be modifying this 
        dict, and shouldn't add new keys, nor delete existing keys.
        
        TODO: add comments stating which parameters are input, output, expected types
        
        TODO: initialization isn't consistent yet. Need to decide whether to
              use None, or an explicit initialization key
              
        :param hooks: A :class:`SimHooks` or similar instance
        
        .. warning:: Don't put invalid floats in here, or this structure
                     is no longer JSON serializable!
    '''
    global hal_data, hal_newdata_sem
    hal_newdata_sem = None
    
    hal_data.clear()
    hal_data.update({

        'alliance_station': constants.kHALAllianceStationID_red1,

        'time': {
            'has_source': False,

            # Used to compute getFPGATime
            'program_start': hooks.getTime(),

            # Used to compute getMatchTime -- set to return value of getFPGATime()
            'match_start': None,
        },
        


        # You should not modify these directly, instead use the mode_helpers!
        'control': {
            'has_source': False,
            'enabled': False,
            'autonomous': False,
            'test': False,
            'eStop': False,
            'fms_attached': False,
            'ds_attached': False
        },
                     
        # key:   resource type
        # value: list of instance numbers
        'reports': NotifyDict({}),

        # See driver station notes above

        # Joysticks are stored numbered 0-5.
        # buttons are stored as booleans
        # axes are stored as values between -1 and 1
        # povs are stored as integer values
        'joysticks': [{
            'has_source': False,
            'buttons': [None] + [False]*12, # numbered 1-12 -- 0 is ignored
            'axes':    [0]*constants.kMaxJoystickAxes,  # x is 0, y is 1, .. 
            'povs':    [-1]*constants.kMaxJoystickPOVs  # integers
        
        } for _ in range(6)],

        

        'fpga_button': False,
        'error_data': None,

        # built-in accelerometer on roboRIO
        'accelerometer': {
            'has_source': False,
            'active': False,
            'range': 0,
            'x': 0,
            'y': 0,
            'z': 0
        },

        # global for all
        'analog_sample_rate': 1024.0, # need a better default

        # 8 analog channels, each is a dictionary.

        'analog_out': [NotifyDict({
            'initialized': False,
            'voltage': 0.0

        }) for _ in range(8)],

        # TODO: make this easier to use
        'analog_in': [NotifyDict({
            'has_source': False,
            'initialized': False,
            'avg_bits': 0,
            'oversample_bits': 0,
            'value': 0,
            'avg_value': 0,
            'voltage': 0,
            'avg_voltage': 0,
            'lsb_weight': 1,    # TODO: better default
            'offset': 65535,    # TODO: better default

            'accumulator_initialized': False,
            'accumulator_center': 0,
            'accumulator_value': 0,
            'accumulator_count': 1, # don't make zero, or divide by zero error occurs
            'accumulator_deadband': 0,

        }) for _ in range(8)],

        'analog_trigger': [{
            'has_source': False,
            'initialized': False,
            'port': 0,
            # trigger values
            'trig_lower': None,
            'trig_upper': None,
            'trig_type': None, # 'averaged' or 'filtered'
            'trig_state': False,

        } for _ in range(8)],

        # compressor control is here
        'compressor': NotifyDict({
            'has_source': False,
            'initialized': False,
            'on': False,
            'closed_loop_enabled': False,
            'pressure_switch': False,
            'current': 0.0
        }),
                
        # digital stuff here
        
        # pwm contains dicts with keys: value, period_scale
        # -> value isn't sane
        'pwm': [NotifyDict({
            'initialized': False,
            'type': None,   # string value set by HALReport: jaguar, victor, talon, etc
            'raw_value': 0, # raw value that is used by wpilib represents the hardware PWM value
            'value':0,      # value is the PWM value that user set from -1 to 1 (but it might not be exactly what you expect)
            'period_scale': None,
            'zero_latch': False,

        }) for _ in range(20)],

        'pwm_loop_timing': 40, # this is the value the roboRIO returns
               
        # for pwm attached to a DIO
        'd0_pwm': [None]*6, # dict with keys: duty_cycle, pin
        'd0_pwm_rate': None,
                
        'relay': [NotifyDict({
            'initialized': False,
            'fwd': False,
            'rev': False,

        }) for _ in range(8)],

        #Keep track of used MXP dio ports
        'mxp': [{
            'initialized': False,

        } for _ in range(16)],
                
        'dio': [NotifyDict({
            'has_source': False,
            'initialized': False,
            'value': False,
            'pulse_length': None,
            'is_input': False
            
        }) for _ in range(26)],
        
        'encoder': [{
            'has_source': False,
            'initialized': False,
            'config': {}, # dictionary of pins/modules
            'count': 0,
            'period': sys.float_info.max,
            'max_period': 0,
            'direction': False,
            'reverse_direction': False,
            'samples_to_average': 0,

        } for _ in range(4)],
        
        # There is a lot of config involved here... 
        'counter': [{
            'has_source': False,
            'initialized': False,
            'count': 0,
            'period': sys.float_info.max,
            'max_period': 0,
            'direction': False,
            'reverse_direction': False,
            'samples_to_average': 0,
            'mode': 0,
            'average_size': 0,
            
            'up_source_channel': 0,
            'up_source_trigger': False,
            'down_source_channel': 0,
            'down_source_trigger': False,
            
            'update_when_empty': False,
            
            'up_rising_edge': False,
            'up_falling_edge': False,
            'down_rising_edge': False,
            'down_falling_edge': False,
            
            'pulse_length_threshold': 0
            
        } for _ in range(8)],
        
        'user_program_state': None, # starting, disabled, autonomous, teleop, test

        'power': {
            'has_source': False,
            'vin_voltage': 0,
            'vin_current': 0,
            'user_voltage_6v': 6.0,
            'user_current_6v': 0,
            'user_active_6v': False,
            'user_faults_6v': 0,
            'user_voltage_5v': 5.0,
            'user_current_5v': 0,
            'user_active_5v': False,
            'user_faults_5v': 0,
            'user_voltage_3v3': 3.3,
            'user_current_3v3': 0,
            'user_active_3v3': False,
            'user_faults_3v3': 0,
        },

        # solenoid values are True, False 
        'solenoid': [NotifyDict({
            'initialized': False,
            'value': None
        })]*8,

        'pdp': {
            'has_source': False,
            'temperature': 0,
            'voltage': 0,
            'current': [0]*16,
            'total_current': 0,
            'total_power': 0,
            'total_energy': 0
        },
        
        # The key is the device number as an integer. The value is a dictionary
        # that is specific to each CAN device
        'CAN': NotifyDict(),
    })

