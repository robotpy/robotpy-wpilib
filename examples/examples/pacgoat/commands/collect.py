
from wpilib.command import CommandGroup

from commands.set_collection_speed import SetCollectionSpeed
from commands.close_claw import CloseClaw
from commands.set_pivot_setpoint import SetPivotSetpoint
from commands.wait_for_ball import WaitForBall

from subsystems.pivot import Pivot
from subsystems.collector import Collector


class Collect(CommandGroup):
    """Get the robot set to collect balls."""

    def __init__(self, robot):
        super().__init__()
        
        self.addSequential(SetCollectionSpeed(robot, Collector.FORWARD))
        self.addParallel(CloseClaw(robot))
        self.addSequential(SetPivotSetpoint(robot, Pivot.COLLECT))
        self.addSequential(WaitForBall(robot))
