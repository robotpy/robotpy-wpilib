
from wpilib.command import CommandGroup

from .open_claw import OpenClaw
from .set_wrist_setpoint import SetWristSetpoint
from .set_elevator_setpoint import SetElevatorSetpoint

class Place(CommandGroup):
    '''Place a held soda can onto the platform.'''
    
    def __init__(self, robot):
        super().__init__()
        
        self.addSequential(SetElevatorSetpoint(robot, 0.25))
        self.addSequential(SetWristSetpoint(robot, 0))
        self.addSequential(OpenClaw(robot))
