
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

from hal_impl import pwm_helpers

import logging
logger = logging.getLogger('gazebo.pwm')


class SimPWM:

    def __init__(self, channel, pwm_dict):
        
        self.publisher = Controller.get().advertise('simulator/pwm/%s' % channel,
                                                    'gazebo.msgs.Float64')
        
        # Wait for the type to be set, and determine which PWM reverse
        # function to use from that
        def _on_type_set(key, value):
            if value != 'jaguar' and value != 'talon' and value != 'victor':
                logger.warn("Simulation cannot handle unknown pwm type '%s' on channel %s" % (value, channel))
                return
            
            logger.info("Registered %s device on channel %s" % (value, channel))
            pwm_dict.register('value', self.on_value_changed, notify=True)
        
        pwm_dict.register('type', _on_type_set)
        self.pwm_entry = pwm_dict

    def on_value_changed(self, key, value):
        msg = Float64()
        msg.data = self.pwm_entry[value]
        self.publisher.publish(msg)

 