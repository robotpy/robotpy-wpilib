from wpilib.command import Command
from .. import robot

#TODO Check this when done


class SetPivotSetpoint(Command):
    """
    Moves the pivot to a given angle. This command finishes when it is within
    the tolerance, but leaves the PID loop running to maintain the position.
    Other commands using the pivot should make sure they disable PID!
    """

    def __init__(self, setpoint):
        self.requires(robot.pivot)
        self.setpoint = setpoint
        super().__init__()

    def initialize(self):
        """Called just before this Command runs the first time."""
        robot.pivot.enable()
        robot.pivot.setSetpoint(self.setpoint)

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return robot.pivot.onTarget()

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass