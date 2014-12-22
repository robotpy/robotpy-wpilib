
from wpilib.command import Command


class DriveWithJoystick(Command):
    """
    This allows PS3 joystick to drive the robot. It is always running
    except when interrupted by another command.
    """

    def __init__(self, robot):
        super().__init__()
        self.requires(robot.drivetrain)
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        self.robot.drivetrain.tankDriveJoystick(self.robot.oi.getJoystick())

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return False

    def end(self):
        """Called once after isFinished returns true"""
        self.robot.drivetrain.stop()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()