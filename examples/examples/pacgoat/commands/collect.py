from wpilib.command import CommandGroup
from commands.set_collection_speed import SetCollectionSpeed
from commands.close_claw import CloseClaw
from commands.set_pivot_setpoint import SetPivotSetpoint
from commands.wait_for_ball import WaitForBall
from subsystems.pivot import Pivot
from subsystems.collector import Collector


#TODO Check this when done


class Collect(CommandGroup):
    """Get the robot set to collect balls."""

    def __init__(self):
        self.addSequential(SetCollectionSpeed(Collector.FORWARD))
        self.addParallel(CloseClaw())
        self.addSequential(SetPivotSetpoint(Pivot.COLLECT))
        self.addSequential(WaitForBall())
        super().__init__()
