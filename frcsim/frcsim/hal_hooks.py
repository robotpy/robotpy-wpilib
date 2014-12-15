
from hal_impl.data import hal_data

class GazeboSimHooks:

    def __init__(self, timer):
        self.tm = timer

    #
    # Hook functions
    #
    
    def getTime(self):
        return self.tm.simTime
    
    def getFPGATime(self):
        return int((self.tm.simTime - hal_data['program_start']) * 1000000)
    
    def delayMillis(self, ms):
        self.tm.wait(.001*ms)
    
    def delaySeconds(self, s):
        self.tm.wait(s)
