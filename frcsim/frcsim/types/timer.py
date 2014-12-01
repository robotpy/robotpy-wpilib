
import logging
import threading

from ..msgs.float64_pb2 import Float64

logger = logging.getLogger('frcsim.timer')

class Timer:

    def __init__(self, controller):

        self.cond = threading.Condition()
        controller.subscribe('time', 'gazebo.msgs.Float64', self.on_time)

        # wait for time before returning
        logger.info("Waiting for first timestamp from gazebo")
        
        with self.cond:
            self.cond.wait()
            
        logger.info("Time acquired (simulation time is %s)" % self.simTime)

    def on_time(self, msg):
        with self.cond:
            self.simTime = Float64.FromString(msg).data 
            self.cond.notify_all()

    def wait(self, seconds):

        start = self.simTime

        while self.simTime - start < seconds:
            with self.cond:
                self.cond.wait()

