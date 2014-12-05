
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

from hal_impl import helpers

import logging
logger = logging.getLogger('gazebo.pwm')


class SimPWM:

    def __init__(self, idx, pwm_dict):
        
        self.publisher = Controller.get().advertise('simulator/pwm/%s' % idx,
                                                    'gazebo.msgs.Float64')
        
        # Wait for the type to be set, and determine which PWM reverse
        # function to use from that
        def _on_type_set(key, value):
            if value == 'jaguar':
                self.convert_fn = helpers.reverseJaguarPWM
            elif value == 'talon':
                self.convert_fn = helpers.reverseTalonPWM
            elif value == 'victor':
                self.convert_fn = helpers.reverseVictorPWM
            else:
                logger.warn("Simulation cannot handle unknown pwm type '%s' on channel %s" % (value, idx))
                return
            
            logger.info("Registered %s device on channel %s" % (value, idx))
            pwm_dict.register('value', self.on_value_changed, notify=True)
        
        pwm_dict.register('type', _on_type_set)
        

    def on_value_changed(self, key, value):
        msg = Float64()
        msg.data = self.convert_fn(value)
        self.publisher.publish(msg)

 