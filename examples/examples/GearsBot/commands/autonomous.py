
from wpilib.command import CommandGroup

from .close_claw import CloseClaw
from .drive_straight import DriveStraight
from .pickup import Pickup
from .place import Place
from .prepare_to_pickup import PrepareToPickup
from .set_distance_to_box import SetDistanceToBox
from .set_wrist_setpoint import SetWristSetpoint


class Autonomous(CommandGroup):
    '''
    The main autonomous command to pickup and deliver the
    soda to the box
    '''
    
    def __init__(self, robot):
        super().__init__()
        
        self.addSequential(PrepareToPickup(robot))
        self.addSequential(Pickup(robot))
        self.addSequential(SetDistanceToBox(robot, 0.10))
        #self.addSequential(DriveStraight(robot, 4)) # Use Encoders if ultrasonic is broken
        self.addSequential(Place(robot))
        self.addSequential(SetDistanceToBox(robot, 0.60))
        #self.addSequential(DriveStraight(robot, -2)) # Use Encoders if ultrasonic is broken
        self.addParallel(SetWristSetpoint(robot, -45))
        self.addSequential(CloseClaw(robot))