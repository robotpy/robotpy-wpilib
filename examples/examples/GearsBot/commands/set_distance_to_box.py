
import wpilib
from wpilib.command import Command

class SetDistanceToBox(Command):
    '''
    Drive until the robot is the given distance away from the box. Uses a local
    PID controller to run a simple PID loop that is only enabled while this
    command is running. The input is the averaged values of the left and right
    encoders.
    '''
    
    def __init__(self, robot, distance):
        super().__init__()
        self.robot = robot
        
        self.requires(self.robot.drivetrain)
        self.pid = wpilib.PIDController(-2, 0, 0,
                                        lambda: self.robot.drivetrain.getDistanceToObstacle(),
                                        lambda d: self.robot.drivetrain.driveManual(d, d))
        self.pid.setAbsoluteTolerance(0.01)
        self.pid.setSetpoint(distance)
        
    def initialize(self):
        '''Called just before this Command runs the first time'''
        
        # Get everything in a safe starting state.
        self.robot.drivetrain.reset()
        self.pid.reset()
        self.pid.enable()
    
    def execute(self):
        '''Called repeatedly when this Command is scheduled to run'''
        
    def isFinished(self):
        '''Make this return true when this Command no longer needs to run execute()'''
        return self.pid.onTarget()
    
    def end(self):
        '''Called once after isFinished returns true'''
        
        # Stop PID and the wheels
        self.pid.disable()
        self.robot.drivetrain.driveManual(0, 0)
        
    def interrupted(self):
        '''Called when another command which requires one or more of the same
           subsystems is scheduled to run'''
        self.end()
