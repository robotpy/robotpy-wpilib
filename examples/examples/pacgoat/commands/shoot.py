
from wpilib.command import CommandGroup

from subsystems.collector import Collector

from commands.extend_shooter import ExtendShooter
from commands.set_collection_speed import SetCollectionSpeed
from commands.wait_for_pressure import WaitForPressure
from commands.open_claw import OpenClaw


class Shoot(CommandGroup):
    """Shoot the ball at the current angle."""

    def __init__(self, robot):
        super().__init__()
        self.addSequential(WaitForPressure(robot))
        self.addSequential(SetCollectionSpeed(robot, Collector.STOP))
        self.addSequential(OpenClaw(robot))
        self.addSequential(ExtendShooter(robot))
