
from wpilib.command import Command


class ExampleCommand(Command):

    def __init__(self, robot, name=None, timeout=None):
        """The Command's constructor"""
        super().__init__(name, timeout)
        #Signal that we require ExampleSubsystem
        self.requires(robot.example_subsystem)
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return False

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        pass
