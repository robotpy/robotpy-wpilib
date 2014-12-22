
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

import logging
logger = logging.getLogger('gazebo.relay')

class SimSolenoid:

    def __init__(self, channel, solenoid_dict):
        
        self.publisher = Controller.get().advertise('simulator/pneumatic/%s/%s' % (0, channel),
                                                    'gazebo.msgs.Float64')
        
        logger.info("Registered solenoid device on channel %s" % (channel,))
        solenoid_dict.register('value', self.on_value_changed, notify=True)

    def on_value_changed(self, key, value):
        
        msg = Float64()
        msg.data = 1.0 if value else -1.0
        self.publisher.publish(msg)

