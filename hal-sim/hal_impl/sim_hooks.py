
import time
from .data import hal_data

class SimHooks:
    '''
        These are useful hooks to override for simulations
    
        To use your own hook, set hal_impl.functions.hooks
    '''
    
    #
    # Hook functions
    #
    
    def getTime(self):
        return time.monotonic()
    
    def getFPGATime(self):
        return int((time.monotonic() - hal_data['time']['program_start']) * 1000000)
    
    def delayMillis(self, ms):
        time.sleep(.001*ms)
    
    def delaySeconds(self, s):
        time.sleep(s)
        
        
    
    
    
    
    