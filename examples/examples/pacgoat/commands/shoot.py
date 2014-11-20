from wpilib.command import CommandGroup

from subsystems.collector import Collector

from commands.extend_shooter import ExtendShooter
from commands.set_collection_speed import SetCollectionSpeed
from commands.wait_for_pressure import WaitForPressure
from commands.open_claw import OpenClaw

#TODO Check this when done


class Shoot(CommandGroup):
    """Shoot the ball at the current angle."""

    def __init__(self):
        self.addSequential(WaitForPressure())
        self.addSequential(SetCollectionSpeed(Collector.STOP))
        self.addSequential(OpenClaw())
        self.addSequential(ExtendShooter)
        super().__init__()