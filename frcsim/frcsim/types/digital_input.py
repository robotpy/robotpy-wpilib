
from ..controller import Controller
from ..msgs.bool_pb2 import Bool

import logging
logger = logging.getLogger('gazebo.dio')

class SimDigitalInput:

    def __init__(self, channel, digital_dict):
        self.digital_dict = digital_dict
        Controller.get().subscribe('simulator/dio/%s' % channel,
                                   'gazebo.msgs.Bool',
                                   self.on_message)
        digital_dict["has_source"] = True
        logger.info("Registered digital input device on channel %s", channel)

    def on_message(self, msg):
        value = Bool.FromString(msg).data
        self.digital_dict['value'] = value