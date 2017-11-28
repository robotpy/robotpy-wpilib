# validated: 2017-10-23 TW 19addb04cf4a edu/wpi/first/wpilibj/drive/MecanumDrive.java
import hal
import math
from .robotdrivebase import RobotDriveBase
from .vector2d import Vector2d

__all__ = ["MecanumDrive"]


class MecanumDrive(RobotDriveBase):
    """A class for driving Mecanum drive platforms.

    Mecanum drives are rectangular with one wheel on each corner. Each wheel has rollers toed in
    45 degrees toward the front or back. When looking at the wheels from the top, the roller axles
    should form an X across the robot. Each drive() function provides different inverse kinematic
    relations for a Mecanum drive robot.

    Drive base diagram:

    \\_______//
    \\ |   | //
       |   |
    //_|___|_\\
    //       \\


    Each drive() function provides different inverse kinematic relations for a Mecanum drive
    robot. Motor outputs for the right side are negated, so motor direction inversion by the user is
    usually unnecessary.
    """
    def __init__(self, frontLeftMotor, rearLeftMotor, frontRightMotor, rearRightMotor):
        """Construct a MecanumDrive.

        If motors need to be inverted, do so beforehand.
        Motor outputs for the right side are negated, so motor direction inversion
        by the user is usually unnecessary

        :param frontLeftMotor: Front Left Motor
        :param rearLeftMotor: Rear Left Motor
        :param frontRightMotor: Front Right Motor
        :param rearRightMotor: Rear Right Motor
        """
        super().__init__()

        self.frontLeftMotor = frontLeftMotor
        self.rearLeftMotor = rearLeftMotor
        self.frontRightMotor = frontRightMotor
        self.rearRightMotor = rearRightMotor

        self.reported = False

    def driveCartesian(self, x, y, rotation, gyroAngle=0.0):
        """Drive method for Mecanum platform.

        :param x: The speed that the robot should drive in the X direction. [-1.0..1.0]
        :param y: The speed that the robot should drive in the Y direction. [-1.0..1.0]
        :param rotation: The rate of rotation for the robot that is completely independent of the
        translation. [-1.0..1.0]
        :param gyroAngle: The current angle reading from the gyro in degrees around the Z axis. Use 
        this to implement field-oriented controls.
        """
        if not self.reported:
            hal.report(hal.UsageReporting.kResourceType_RobotDrive,
                       4,
                       hal.UsageReporting.kRobotDrive_MecanumCartesian)
            self.reported = True

        x = RobotDriveBase.limit(x)
        x = RobotDriveBase.applyDeadband(x, self.deadband)

        y = RobotDriveBase.limit(y)
        y = RobotDriveBase.applyDeadband(y, self.deadband)

        # Compensate for gyro angle
        input = Vector2d(x, y)
        input.rotate(gyroAngle)

        wheelSpeeds = [
            # Front Left
            input.x + input.y + rotation,
            # Rear Left
            -input.x + input.y + rotation,
            # Front Right
            input.x - input.y + rotation,
            # Rear Right
            -input.x - input.y + rotation
        ]

        RobotDriveBase.normalize(wheelSpeeds)

        wheelSpeeds = [speed * self.maxOutput for speed in wheelSpeeds]

        self.frontLeftMotor.set(wheelSpeeds[0])
        self.rearLeftMotor.set(wheelSpeeds[1])
        self.frontRightMotor.set(wheelSpeeds[2])
        self.rearRightMotor.set(wheelSpeeds[3])

        self.feed()

    def drivePolar(self, magnitude, angle, rotation):
        """Drive method for Mecanum platform.

        :param magnitude: The speed that the robot should drive in a given direction. [-1.0..1.0]
        :param angle: The direction the robot should drive in degrees. 0.0 is straight ahead. The
        direction and maginitude are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is completely independent of the
        magnitude or direction. [-1.0..1.0]
        """
        if not self.reported:
            hal.report(hal.UsageReporting.kResourceType_RobotDrive,
                       4,
                       hal.UsageReporting.kRobotDrive_MecanumPolar)
            self.reported = True

        magnitude = RobotDriveBase.limit(magnitude) * math.sqrt(2)

        self.driveCartesian(magnitude * math.cos(math.radians(angle)),
                            magnitude * math.sin(math.radians(angle)),
                            rotation, 0.0)

    def stopMotor(self):
        self.frontLeftMotor.stopMotor()
        self.rearLeftMotor.stopMotor()
        self.frontRightMotor.stopMotor()
        self.rearRightMotor.stopMotor()
        self.feed()

    def getDescription(self):
        return "Mecanum Drive"
