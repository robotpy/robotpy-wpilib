
from wpilib.command import Command

class CloseClaw(Command):
    """Close the claw.

    NOTE: It doesn't wait for the claw to close since there is no sensor to detect that.
    """

    def __init__(self, robot):
        super().__init__()
        self.requires(robot.collector)
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.collector.close()

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return True

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass