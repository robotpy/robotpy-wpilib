#
# All data that passes through the HAL comes to/from here
#

from hal import constants
import time

hal_data = {
    # don't fill this out, fill out the version in reset_hal_data
}


def reset_hal_data():
    '''
        Intended to be used by the test runner or simulator
        
        Subject to change until the simulator is fully developed, as the
        usefulness of some of this isn't immediately clear yet.
        
        TODO: add comments stating which parameters are input, output, expected types
        
        TODO: initialization isn't consistent yet. Need to decide whether to
              use None, or an explicit initialization key
    '''
    global hal_data
    hal_data = {

        'alliance_station': constants.kHALAllianceStationID_red1,
        'program_start': time.monotonic(),

        'control': {
            'enabled': False,
            'autonomous': False,
            'test': False,
            'eStop': False,
            'fms_attached': False,
            'ds_attached': False
        },

        # Joysticks are stored numbered 1-4. Element 0 is ignored.
        # buttons are stored as booleans
        # axes are stored as values between -1 and 1
        # povs are stored as integer values
        'joysticks': [None] + [
            {
                'buttons': [None]+[False]*12, # numbered 1-12. element 0 is ignored
                'axes':    [0]*constants.kMaxJoystickAxes,  # x is 0, y is 1, .. 
                'povs':    [-1]*constants.kMaxJoystickPOVs  # integers
            }
        ]*6,

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
        }]*2,

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
            'accumulator_count': 0,
            'accumulator_deadband': 0,
            
            # trigger values
            'trig_lower': None,
            'trig_upper': None,
            'trig_type': None, # 'averaged' or 'filtered'
            'trig_state': False,
        }]*8,

        # compressor control is here
        'compressor': {
            'enabled': False,
            'closed_loop_enabled': True,
            'pressure_switch': False,
            'current': 0.0
        },
                
        # digital stuff here
        
        # pwm contains dicts with keys: value, period_scale
        # -> value isn't sane
        'pwm': [None]*20,
        'pwm_loop_timing': 40, # this is the value the roboRIO returns
               
        # for pwm attached to a DIO
        'd0_pwm': [None]*6, # dict with keys: duty_cycle, pin
        'd0_pwm_rate': None,
                
        'relay': [{
            'fwd': False,
            'rev': False,
        }]*8,
                
        'dio': [None]*10, # dict keys: value, is_input, pulse_length
        
        'user_program_state': None, # starting, disabled, autonomous, teleop, test

        'power': {
            'vin_voltage': 0,
            'vin_current': 0,
            'user_voltage_6v': 6.0,
            'user_current_6v': 0,
            'user_voltage_5v': 5.0,
            'user_current_5v': 0,
            'user_voltage_3v3': 3.3,
            'user_current_3v3': 0
        },

        # solenoid values are True, False  
        'solenoid': [None]*8,

        'pdp': {
            'temperature': 0,
            'voltage': 0,
            'current': [0]*16
        }
    }

reset_hal_data()
