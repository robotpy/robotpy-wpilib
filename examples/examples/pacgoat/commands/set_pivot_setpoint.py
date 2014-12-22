
from wpilib.command import Command


class SetPivotSetpoint(Command):
    """
    Moves the pivot to a given angle. This command finishes when it is within
    the tolerance, but leaves the PID loop running to maintain the position.
    Other commands using the pivot should make sure they disable PID!
    """

    def __init__(self, robot, setpoint):
        super().__init__()
        self.requires(robot.pivot)
        self.setpoint = setpoint
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.pivot.enable()
        self.robot.pivot.setSetpoint(self.setpoint)

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return self.robot.pivot.onTarget()

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass