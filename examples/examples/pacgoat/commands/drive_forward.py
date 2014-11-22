from wpilib.command import Command

#TODO Check this when done

class DriveForward(Command):
    """
    This command drives the robot over a given distance with simple proportional
    control. This command will drive a given distance limiting to a maximum speed.
    """
    drive_forward_speed = 0
    distance = 0
    error = 0
    TOLERANCE = .1
    KP = -1.0/5.0

    def __init__(self, robot, dist=10, max_speed=.5):
        """The constructor"""
        super().__init__()
        #Signal that we require ExampleSubsystem
        self.requires(robot.drivetrain)
        self.distance = dist
        self.drive_forward_speed = max_speed
        self.robot = robot

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.drivetrain.get_right_encoder().reset()
        self.setTimeout(2)

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        error = self.distance - self.robot.drivetrain.get_right_encoder().get()
        if self.drive_forward_speed * self.KP * error >= self.drive_forward_speed:
            self.robot.drivetrain.tank_drive(self.drive_forward_speed, self.drive_forward_speed)
        else:
            speed = self.drive_forward_speed * self.KP * error
            self.robot.drivetrain.tank_drive(speed, speed)

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return abs(self.error) <= self.TOLERANCE or self.isTimedOut()

    def end(self):
        """Called once after isFinished returns true"""
        self.robot.drivetrain.stop()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()