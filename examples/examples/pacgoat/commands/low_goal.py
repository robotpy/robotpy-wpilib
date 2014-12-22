
from wpilib.command import CommandGroup

from subsystems.collector import Collector
from subsystems.pivot import Pivot

from .extend_shooter import ExtendShooter
from .set_collection_speed import SetCollectionSpeed
from .set_pivot_setpoint import SetPivotSetpoint


class LowGoal(CommandGroup):
    """Spit the ball out into the low goal assuming that the robot is in front of it."""

    def __init__(self, robot):
        super().__init__()
        self.addSequential(SetPivotSetpoint(robot, Pivot.LOW_GOAL))
        self.addSequential(SetCollectionSpeed(robot, Collector.REVERSE))
        self.addSequential(ExtendShooter(robot))
