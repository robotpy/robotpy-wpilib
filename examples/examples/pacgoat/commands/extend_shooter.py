
from wpilib.command import Command


class ExtendShooter(Command):
    """Extend the shooter and retract it after a second."""

    def __init__(self, robot):
        super().__init__()
        self.requires(robot.shooter)
        self.setTimeout(1)
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.shooter.extendBoth()

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return self.isTimedOut()

    def end(self):
        """Called once after isFinished returns true"""
        self.robot.shooter.retractBoth()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()