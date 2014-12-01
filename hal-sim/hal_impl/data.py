#
# All data that passes through the HAL comes to/from here
#

from hal import constants
import time

#: Dictionary of all robot data
hal_data = {
    # don't fill this out, fill out the version in reset_hal_data
}

#: A multiwait object. Use hal.giveMultiWait() to set this when
#: driver station related data has been updated
hal_newdata_sem = None


def reset_hal_data(hooks):
    '''
        Intended to be used by the test runner or simulator
        
        Subject to change until the simulator is fully developed, as the
        usefulness of some of this isn't immediately clear yet.
        
        TODO: add comments stating which parameters are input, output, expected types
        
        TODO: initialization isn't consistent yet. Need to decide whether to
              use None, or an explicit initialization key
              
        :param hooks: A :class:`SimHooks` or similar instance
    '''
    global hal_data, hal_newdata_sem
    hal_newdata_sem = None
    
    hal_data.clear()
    hal_data.update({

        'alliance_station': constants.kHALAllianceStationID_red1,
        
        # Used to compute getFPGATime
        'program_start': hooks.getTime(),
        
        # Used to compute getMatchTime -- set to return value of getFPGATime()
        'match_start': None,

        # See driver station notes above
        'control': {
            'enabled': False,
            'autonomous': False,
            'test': False,
            'eStop': False,
            'fms_attached': False,
            'ds_attached': False
        },
                     
        # key:   resource type
        # value: list of instance numbers
        'reports': {},

        # See driver station notes above

        # Joysticks are stored numbered 0-5.
        # buttons are stored as booleans
        # axes are stored as values between -1 and 1
        # povs are stored as integer values
        'joysticks': [{
            'buttons': [False]*12, # numbered 0-11
            'axes':    [0]*constants.kMaxJoystickAxes,  # x is 0, y is 1, .. 
            'povs':    [-1]*constants.kMaxJoystickPOVs  # integers
        
        } for _ in range(6)],

        

        'fpga_button': False,
        'error_data': None,

        # built-in accelerometer on roboRIO
        'accelerometer': {
            'active': False,
            'range': 0,
            'x': 0,
            'y': 0,
            'z': 0
        },

        # global for all
        'analog_sample_rate': 1024.0, # need a better default

        # 8 analog channels, each is a dictionary.

        'analog_out': [{
            'initialized': False,
            'voltage': 0.0

        } for _ in range(2)],

        # TODO: make this easier to use
        'analog_in': [{
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
            
            # trigger values
            'trig_lower': None,
            'trig_upper': None,
            'trig_type': None, # 'averaged' or 'filtered'
            'trig_state': False,

        } for _ in range(8)],

        # compressor control is here
        'compressor': {
            'initialized': False,
            'on': False,
            'closed_loop_enabled': False,
            'pressure_switch': False,
            'current': 0.0
        },
                
        # digital stuff here
        
        # pwm contains dicts with keys: value, period_scale
        # -> value isn't sane
        'pwm': [{
            'initialized': False,
            'value': 0,
            'period_scale': None,
            'zero_latch': False,

        } for _ in range(20)],

        'pwm_loop_timing': 40, # this is the value the roboRIO returns
               
        # for pwm attached to a DIO
        'd0_pwm': [None]*6, # dict with keys: duty_cycle, pin
        'd0_pwm_rate': None,
                
        'relay': [{
            'fwd': False,
            'rev': False,

        } for _ in range(8)],
                
        'dio': [{
            'initialized': False,
            'value': 0,
            'pulse_length': None,
            'is_input': False
        } for _ in range(10)],
        
        'encoder': [{
            'initialized': False,
            'config': [None]*6, # list of pins/modules
            'count': 0,
            'period': 0,
            'max_period': 0,
            'direction': False,
            'reverse_direction': False,
            'samples_to_average': 0,

        } for _ in range(4)],
        
        # There is a lot of config involved here... 
        'counter': [{
            'initialized': False,
            'count': 0,
            'period': 0,
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
        'solenoid': [None]*8,

        'pdp': {
            'temperature': 0,
            'voltage': 0,
            'current': [0]*16
        }
    })

