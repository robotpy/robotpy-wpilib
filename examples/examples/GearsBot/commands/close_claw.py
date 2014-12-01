
from wpilib.command import Command

class CloseClaw(Command):
    '''
    Closes the claw for one second. Real robots should use sensors, stalling
    motors is BAD!
    '''
    
    def __init__(self, robot):
        super().__init__()
        
        self.robot = robot
        self.requires(self.robot.claw)
        
    def initialize(self):
        '''Called just before this Command runs the first time'''
        self.robot.claw.close()
        
    def execute(self):
        '''Called repeatedly when this Command is scheduled to run'''
        
    def isFinished(self):
        '''Make this return true when this Command no longer needs to run execute()'''
        return self.robot.claw.isGrabbing()
    
    def end(self):
        '''Called once after isFinished returns true'''
        
        # NOTE: Doesn't stop in simulation due to lower friction causing the can to fall out
        # + there is no need to worry about stalling the motor or crushing the can.
        if not self.robot.isSimulation(): 
            self.robot.claw.stop();
            
    def interrupted(self):
        '''Called when another command which requires one or more of the same
           subsystems is scheduled to run'''
        self.end()