from wpilib.command import Command
from .. import robot

#TODO Check this when done

class DriveWithJoystick(Command):
    """
    This allows PS3 joystick to drive the robot. It is always running
    except when interrupted by another command.
    """

    def __init__(self):
        self.requires(robot.drivetrain)
        super().__init__()

    def initialize(self):
        """Called just before this Command runs the first time."""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        robot.drivetrain.tankDrive(robot.Oi.get_joystick())

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return False

    def end(self):
        """Called once after isFinished returns true"""
        robot.drivetrain.stop()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()