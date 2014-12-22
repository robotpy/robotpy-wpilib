
from wpilib.command import Command


class WaitForPressure(Command):
    """
    Wait until the pneumatics are fully pressurized. This command does
    nothing and is intended to be used in command groups to wait for the
    condition.
    """

    def __init__(self, robot):
        super().__init__()
        self.requires(robot.pneumatics)
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return self.robot.pneumatics.isPressurized()

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass