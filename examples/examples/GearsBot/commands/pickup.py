
from wpilib.command import CommandGroup

from .close_claw import CloseClaw
from .set_wrist_setpoint import SetWristSetpoint
from .set_elevator_setpoint import SetElevatorSetpoint

class Pickup(CommandGroup):
    
    def __init__(self, robot):
        super().__init__()
        
        self.addSequential(CloseClaw(robot))
        self.addParallel(SetWristSetpoint(robot, -45))
        self.addSequential(SetElevatorSetpoint(robot, 0.25))
