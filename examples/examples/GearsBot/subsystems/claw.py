
import wpilib
from wpilib.command import Subsystem

class Claw(Subsystem):
    '''
    The claw subsystem is a simple system with a motor for opening and closing.
    If using stronger motors, you should probably use a sensor so that the
    motors don't stall. 
    '''
    
    def __init__(self):
        super().__init__()
        
        self.motor = wpilib.Victor(7)
        self.contact = wpilib.DigitalInput(5)
        
        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator("Claw", "Motor", self.motor)
        wpilib.LiveWindow.addActuator("Claw", "Limit Switch", self.contact)
    
    def log(self):
        pass
    
    def open(self):
        '''Set the claw motor to move in the open direction.'''
        self.motor.set(-1)
        
    def close(self):
        '''Set the claw motor to move in the close direction.'''
        self.motor.set(1)
        
    def stop(self):
        '''Stops the claw motor from moving.'''
        self.motor.set(0)
        
    def isGrabbing(self):
        '''Return true when the robot is grabbing an object hard enough
           to trigger the limit switch'''
        return self.contact.get()
