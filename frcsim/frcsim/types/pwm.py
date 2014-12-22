
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

import logging
logger = logging.getLogger('gazebo.pwm')


class SimPWM:

    def __init__(self, channel, pwm_dict):
        
        self.publisher = Controller.get().advertise('simulator/pwm/%s' % channel,
                                                    'gazebo.msgs.Float64')
        
        logger.info("Registered PWM device on channel %s" % channel)
        pwm_dict.register('value', self.on_value_changed, notify=True)
        

    def on_value_changed(self, key, value):
        msg = Float64()
        msg.data = value
        self.publisher.publish(msg)

