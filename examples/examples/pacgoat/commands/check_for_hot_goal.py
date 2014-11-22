from wpilib.command import Command

#TODO finish this


class CheckForHotGoal(Command):
    """
    This command looks for the hot goal and waits until it's detected or timed
    out. The timeout is because it's better to shoot and get some autonomous
    points than get none. When called sequentially, this command will block until
    the hot goal is detected or until it is timed out.
    """
    def __init__(self, time, robot):
        self.robot = robot
        self.setTimeout(time)
        super().__init__()

    def initialize(self):
        pass

    def execute(self):
        pass

    def isFinished(self):
        return self.isTimedOut() or self.robot.shooter.goal_is_hot()

    def end(self):
        pass

    def interrupted(self):
        self.end()
