
from wpilib.command import Command

class DriveForward(Command):
    """
    This command drives the robot over a given distance with simple proportional
    control. This command will drive a given distance limiting to a maximum speed.
    """
    
    TOLERANCE = .1
    KP = -1.0/5.0

    def __init__(self, robot, dist=10, max_speed=.5):
        """The constructor"""
        super().__init__()
        # Signal that we require ExampleSubsystem
        self.requires(robot.drivetrain)
        self.distance = dist
        self.driveForwardSpeed = max_speed
        self.robot = robot
        self.error = 0

    def initialize(self):
        """Called just before this Command runs the first time."""
        self.robot.drivetrain.getRightEncoder().reset()
        self.setTimeout(2)

    def execute(self):
        """Called repeatedly when this Command is scheduled to run"""
        self.error = self.distance - self.robot.drivetrain.getRightEncoder().get()
        if self.driveForwardSpeed * self.KP * self.error >= self.driveForwardSpeed:
            self.robot.drivetrain.tankDriveManual(self.driveForwardSpeed,
                                                  self.driveForwardSpeed)
        else:
            self.robot.drivetrain.tankDriveManual(self.driveForwardSpeed * self.KP * self.error,
                                                  self.driveForwardSpeed * self.KP * self.error)

    def isFinished(self):
        """Make this return true when this Command no longer needs to run execute()"""
        return abs(self.error) <= self.TOLERANCE or self.isTimedOut()

    def end(self):
        """Called once after isFinished returns true"""
        self.robot.drivetrain.stop()

    def interrupted(self):
        """Called when another command which requires one or more of the same subsystems is scheduled to run."""
        self.end()