from wpilib.command import Command
#TODO Check this when done


class SetCollectionSpeed(Command):
    """
    This command sets the collector rollers spinning a the given speed. Since
    there is no sensor for detecting speed, it finishes immediately. As a result,
    the spinners may still be adjusting their speed.
    """

    speed = 0

    def __init__(self, robot, speed):
        self.requires(robot.collector)
        self.speed = speed
        self.robot = robot
        super().__init__()

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.collector.set_speed(self.speed)

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