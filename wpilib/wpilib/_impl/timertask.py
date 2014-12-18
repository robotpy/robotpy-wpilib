'''
    An implementation of java.util.TimerTask which is needed for
    the PID Controller
'''

import threading
from ..timer import Timer


class TimerTask(threading.Thread):
    
    def __init__(self, name, period, task_fn):
        super().__init__(name=name, daemon=True)
        self.period = period
        self.task_fn = task_fn
        
        self.stopped = False
    
    def cancel(self):
        self.stopped = True
        self.join()
    
    def run(self):
        
        period = self.period
        wait_til = Timer.getFPGATimestamp() + period
        
        while not self.stopped:
            
            now = Timer.getFPGATimestamp()
            Timer.delay(wait_til - now)
            
            if self.stopped:
                break
            
            self.task_fn()
            
            wait_til += period
    