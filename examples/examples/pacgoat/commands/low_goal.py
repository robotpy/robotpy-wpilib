from wpilib.command import CommandGroup

from ..subsystems.collector import Collector
from ..subsystems.pivot import Pivot

from .extend_shooter import ExtendShooter
from .set_collection_speed import SetCollectionSpeed
from .set_pivot_setpoint import SetPivotSetpoint

#TODO Check this when done

class LowGoal(CommandGroup):
    """Spit the ball out into the low goal assuming that the robot is in front of it."""

    def __init__(self):
        self.addSequential(SetPivotSetpoint(Pivot.LOW_GOAL))
        self.addSequential(SetCollectionSpeed(Collector.REVERSE))
        self.addSequential(ExtendShooter())
        super().__init__()
