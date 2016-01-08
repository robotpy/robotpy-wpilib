
from wpilib.buttons import Trigger


#This is a template Trigger, TriggerName should, of course, be replaced by the name of your desired Trigger
class TriggerName(Trigger):
    
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    def get(self):
        return False
