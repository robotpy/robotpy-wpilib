from wpilib.command import Command
from global_vars import subsystems

#TODO Check this when done

class ExtendShooter(Command):
    """Extend the shooter and retract it after a second."""

    def __init__(self):
        self.requires(subsystems["shooter"])
        self.setTimeout(1)
        super().__init__()

    def initialize(self):
        """Called just before this Command runs the first time."""
        subsystems["shooter"].extend_both()

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return self.isTimedOut()

    def end(self):
        """Called once after isFinished returns true"""
        subsystems["shooter"].extend_both()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()