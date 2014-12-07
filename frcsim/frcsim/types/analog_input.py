
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

import logging
logger = logging.getLogger('gazebo.pwm')

class SimAnalogInput:

    def __init__(self, channel, analog_dict):
        self.analog_dict = analog_dict
        Controller.get().subscribe('simulator/analog/%s' % channel,
                                   'gazebo.msgs.Float64',
                                   self.on_message)
        
        logger.info("Registered analog input device on channel %s" % channel)

    def on_message(self, msg):
        value = Float64.FromString(msg).data
        self.analog_dict['voltage'] = value
        self.analog_dict['avg_voltage'] = value
        
        
