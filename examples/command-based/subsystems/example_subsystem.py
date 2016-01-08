
from wpilib.command import Subsystem


#This is a template Subsystem, SubsystemName should, of course, be replaced
# with the name of your desired Subsystem
class ExampleSubsystem(Subsystem):

    def __init__(self, robot, name = None):
        super().__init__(name = name)
        self.robot = robot
    
    #Put methods for controlling this subsystem here.
    # Call these from Commands.

    def initDefaultCommand(self):
        #Set the default command for a subsystem here.
        #setDefaultCommand(ExampleCommand())
        pass
