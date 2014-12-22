
from ..controller import Controller
from ..msgs.float64_pb2 import Float64

import logging
logger = logging.getLogger('gazebo.relay')

class SimRelay:

    def __init__(self, channel, relay_dict):
        
        self.relay_dict = relay_dict
        self.publisher = Controller.get().advertise('simulator/relay/%s' % channel,
                                                    'gazebo.msgs.Float64')
        
        logger.info("Registered relay device on channel %s" % (channel,))
        relay_dict.register('fwd', self.on_value_changed, notify=True)
        relay_dict.register('rev', self.on_value_changed, notify=True)


    def on_value_changed(self, key, value):
        
        value = (1.0 if self.relay_dict['fwd'] else 0.0) + \
                (-1.0 if self.relay_dict['rev'] else 0.0)
        
        msg = Float64()
        msg.data = value
        self.publisher.publish(msg)

