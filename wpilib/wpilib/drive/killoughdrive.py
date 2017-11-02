# validated: 2017-10-23 TW 19addb04cf4a edu/wpi/first/wpilibj/drive/KilloughDrive.java
from .robotdrivebase import RobotDriveBase
from .vector2d import Vector2d

import math

__all__ = ["KilloughDrive"]


class KilloughDrive(RobotDriveBase):
    def __init__(self, leftMotor, rightMotor, backMotor, leftMotorAngle=120, rightMotorAngle=60, backMotorAngle=270):
        """Construct a Killough drive with the given motors and default motor angles.

            The default motor angles are 120, 60, and 270 degrees for the left, right, and back motors
            respectively, which make the wheels on each corner parallel to their respective opposite sides.

            If a motor needs to be inverted, do so before passing it in.

            :param leftMotor: The motor on the left corner.
            :param rightMotor: The motor on the right corner.
            :param backMotor: The motor on the back corner.
        """
        super().__init__()

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.backMotor = backMotor

        self.leftVec = Vector2d(math.cos(math.radians(leftMotorAngle)),
                                math.sin(math.radians(leftMotorAngle)))
        self.rightVec = Vector2d(math.cos(math.radians(rightMotorAngle)),
                                 math.sin(math.radians(rightMotorAngle)))
        self.backVec = Vector2d(math.cos(math.radians(backMotorAngle)),
                                math.sin(math.radians(backMotorAngle)))

        self.reported = False

    def driveCartesian(self, x, y, rotation, gyroAngle=0.0):
        """Drive method for Killough platform

        :param x: The speed that the robot should drive in the X direction [-1.0..1.0]
        :param y: The speed that the robot should drive in the Y direction [-1.0..1.0]
        :param rotation: The rate of rotation for the robot that is completely independent
                         of translation [-1.0..1.0]
        :param gyroAngle: The current angle reading from the gyro. Use this to implement
                          field-oriented controls.
        """

        if not self.reported:
            # hal.report(hal.UsageReporting.kResourceType_RobotDrive,
            #           3,
            #           hal.UsageReporting.kRobotDrive_Curvature)
            self.reported = True

        x = RobotDriveBase.limit(x)
        x = RobotDriveBase.applyDeadband(x, self.deadband)

        y = RobotDriveBase.limit(y)
        y = RobotDriveBase.applyDeadband(y, self.deadband)

        # Compensate for gyro angle
        input = Vector2d(x, y)
        input.rotate(gyroAngle)

        wheelSpeeds = [input.scalarProject(self.leftVec) + rotation,
                       input.scalarProject(self.rightVec) + rotation,
                       input.scalarProject(self.backVec) + rotation]

        RobotDriveBase.normalize(wheelSpeeds)

        self.leftMotor.set(wheelSpeeds[0] * self.maxOutput)
        self.rightMotor.set(wheelSpeeds[1] * self.maxOutput)
        self.backMotor.set(wheelSpeeds[2] * self.maxOutput)

        self.feed()

    def drivePolar(self, magnitude, angle, rotation):
        """Drive method for Killough platform.

        :param magnitude: The speed that the robot should drive in a given direction. [-1.0..1.0]
        :param angle: The direction the robot should drive in degrees. 0.0 is straight ahead. The
        direction and maginitude are independent of the rotation rate.
        :param rotation: The rate of rotation for the robot that is completely independent of the
        magnitude or direction. [-1.0..1.0]
        """
        if not self.reported:
            # hal.report(hal.UsageReporting.kResourceType_RobotDrive,
            #           3,
            #           hal.UsageReporting.kRobotDrive_KilloughPolar)
            self.reported = True

        magnitude = RobotDriveBase.limit(magnitude) * math.sqrt(2)

        self.driveCartesian(magnitude * math.cos(math.radians(angle)), magnitude * math.sin(math.radians(angle)),
                            rotation, 0)

    def stopMotor(self):
        self.leftMotor.stopMotor()
        self.rightMotor.stopMotor()
        self.backMotor.stopMotor()
        self.feed()

    def getDescription(self):
        return "Killough Drive"
