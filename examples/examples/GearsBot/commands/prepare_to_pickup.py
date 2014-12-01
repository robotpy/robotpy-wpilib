
from wpilib.command import CommandGroup

from .open_claw import OpenClaw
from .set_wrist_setpoint import SetWristSetpoint
from .set_elevator_setpoint import SetElevatorSetpoint

class PrepareToPickup(CommandGroup):
    '''Make sure the robot is in a state to pickup soda cans.'''
    
    def __init__(self, robot):
        super().__init__()
        
        self.addParallel(OpenClaw(robot))
        self.addParallel(SetWristSetpoint(robot, 0))
        self.addSequential(SetElevatorSetpoint(robot, 0))
