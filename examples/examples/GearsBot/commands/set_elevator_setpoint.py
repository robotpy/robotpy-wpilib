
from wpilib.command import Command

class SetElevatorSetpoint(Command):
    '''
    Move the elevator to a given location. This command finishes when it is within
    the tolerance, but leaves the PID loop running to maintain the position. Other
    commands using the elevator should make sure they disable PID!
    '''    
    def __init__(self, robot, setpoint):
        super().__init__()
        self.robot = robot
        
        self.setpoint = setpoint
        self.requires(self.robot.elevator)
        
    def initialize(self):
        '''Called just before this Command runs the first time'''
        self.robot.elevator.enable()
        self.robot.elevator.setSetpoint(self.setpoint)
    
    def execute(self):
        '''Called repeatedly when this Command is scheduled to run'''
        
    def isFinished(self):
        '''Make this return true when this Command no longer needs to run execute()'''
        return self.robot.elevator.onTarget()
    
    def end(self):
        '''Called once after isFinished returns true'''
        
    def interrupted(self):
        '''Called when another command which requires one or more of the same
           subsystems is scheduled to run'''
