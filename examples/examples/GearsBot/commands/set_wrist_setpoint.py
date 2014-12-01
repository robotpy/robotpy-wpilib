
from wpilib.command import Command

class SetWristSetpoint(Command):
    '''
    Move the wrist to a given angle. This command finishes when it is within
    the tolerance, but leaves the PID loop running to maintain the position.
    Other commands using the wrist should make sure they disable PID!
    '''    
    def __init__(self, robot, setpoint):
        super().__init__()
        self.robot = robot
        
        self.setpoint = setpoint
        self.requires(self.robot.wrist)
        
    def initialize(self):
        '''Called just before this Command runs the first time'''
        self.robot.wrist.enable()
        self.robot.wrist.setSetpoint(self.setpoint)
    
    def execute(self):
        '''Called repeatedly when this Command is scheduled to run'''
        
    def isFinished(self):
        '''Make this return true when this Command no longer needs to run execute()'''
        return self.robot.wrist.onTarget()
    
    def end(self):
        '''Called once after isFinished returns true'''
        
    def interrupted(self):
        '''Called when another command which requires one or more of the same
           subsystems is scheduled to run'''
