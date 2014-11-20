from wpilib.command import Command
from global_vars import subsystems

#TODO Check this when done


class OpenClaw(Command):
    """Opens the claw."""

    def __init__(self):
        self.requires(subsystems["collector"])
        super().__init__()

    def initialize(self):
        """Called just before this Command runs the first time."""
        subsystems["collector"].open()

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return subsystems["collector"].is_open()

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass