
from wpilib.command import Command

class CheckForHotGoal(Command):
    """
    This command looks for the hot goal and waits until it's detected or timed
    out. The timeout is because it's better to shoot and get some autonomous
    points than get none. When called sequentially, this command will block until
    the hot goal is detected or until it is timed out.
    """
    def __init__(self, time, robot):
        super().__init__()
        self.robot = robot
        self.setTimeout(time)

    def initialize(self):
        """Called just before this Command runs the first time"""
        pass

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        pass

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return self.isTimedOut() or self.robot.shooter.goalIsHot()

    def end(self):
        """Called once after isFinished returns true"""
        pass

    def interrupted(self):
        """Called when another command which requires one or more of the same
        subsystems is scheduled to run"""
        self.end()
