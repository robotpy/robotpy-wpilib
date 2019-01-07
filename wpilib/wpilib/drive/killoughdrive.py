# validated: 2019-01-06 TW a60f312d19ee edu/wpi/first/wpilibj/drive/KilloughDrive.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import math
import hal


from .robotdrivebase import RobotDriveBase
from .vector2d import Vector2d
from ..interfaces.speedcontroller import SpeedController
from ..sendablebuilder import SendableBuilder

__all__ = ["KilloughDrive"]


class KilloughDrive(RobotDriveBase):
    r"""A class for driving Killough drive platforms.

    Killough drives are triangular with one omni wheel on each corner.

    Drive Base Diagram::

          /_____\
         / \   / \
            \ /
            ---

    Each `drive()` function provides different inverse kinematic relations for a Killough drive.
    The default wheel vectors are parallel to their respective opposite sides, but can be overridden.
    See the constructor for more information.

    This library uses the NED axes convention (North-East-Down as external reference in the world
    frame): http://www.nuclearprojects.com/ins/images/axis_big.png.

    The positive X axis points ahead, the positive Y axis points right, and the positive Z axis
    points down. Rotations follow the right-hand rule, so clockwise rotation around the Z axis is
    positive.
    """

    kDefaultLeftMotorAngle = 60.0
    kDefaultRightMotorAngle = 120.0
    kDefaultBackMotorAngle = 270.0

    instances = 0

    def __init__(
        self,
        leftMotor: SpeedController,
        rightMotor: SpeedController,
        backMotor: SpeedController,
        leftMotorAngle: float = kDefaultLeftMotorAngle,
        rightMotorAngle: float = kDefaultRightMotorAngle,
        backMotorAngle: float = kDefaultBackMotorAngle,
    ) -> None:
        """Construct a Killough drive with the given motors and default motor angles.

        Angles are measured in degrees clockwise from the positive X axis.
        
        The default motor angles make the wheels on each corner parallel to their
        respective opposite sides.

        If a motor needs to be inverted, do so before passing it in.

        :param leftMotor: The motor on the left corner.
        :param rightMotor: The motor on the right corner.
        :param backMotor: The motor on the back corner.
        :param leftMotorAngle: The angle of the left wheel's forward direction of travel
        :param rightMotorAngle: The angle of the right wheel's forward direction of travel
        :param backMotorAngle: The angle of the back wheel's forward direction of travel
        """
        assert leftMotor is not None, "Left Motor should not be None"
        assert rightMotor is not None, "Right Motor should not be None"
        assert backMotor is not None, "Back Motor should not be None"
        super().__init__()

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor
        self.backMotor = backMotor

        self.leftVec = Vector2d(
            math.cos(math.radians(leftMotorAngle)),
            math.sin(math.radians(leftMotorAngle)),
        )
        self.rightVec = Vector2d(
            math.cos(math.radians(rightMotorAngle)),
            math.sin(math.radians(rightMotorAngle)),
        )
        self.backVec = Vector2d(
            math.cos(math.radians(backMotorAngle)),
            math.sin(math.radians(backMotorAngle)),
        )

        self.addChild(self.leftMotor)
        self.addChild(self.rightMotor)
        self.addChild(self.backMotor)
        KilloughDrive.instances += 1
        self.setName("KilloughDrive", self.instances)

        self.reported = False

    def driveCartesian(
        self, ySpeed: float, xSpeed: float, zRotation: float, gyroAngle: float = 0.0
    ) -> None:
        """Drive method for Killough platform.

        Angles are measured clockwise from the positive X axis. The robot's speed is independent
        from its angle or rotation rate.

        :param ySpeed: The robot's speed along the Y axis `[-1.0..1.0]`. Right is positive.
        :param xSpeed: The robot's speed along the X axis `[-1.0..1.0]`. Forward is positive.
        :param zRotation: The robot's rotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive.
        :param gyroAngle: The current angle reading from the gyro in degrees around the Z axis. Use
                          this to implement field-oriented controls.
        """

        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                3,
                hal.UsageReporting.kRobotDrive2_KilloughCartesian,
            )
            self.reported = True

        ySpeed = RobotDriveBase.limit(ySpeed)
        ySpeed = RobotDriveBase.applyDeadband(ySpeed, self.deadband)

        xSpeed = RobotDriveBase.limit(xSpeed)
        xSpeed = RobotDriveBase.applyDeadband(xSpeed, self.deadband)

        # Compensate for gyro angle
        input = Vector2d(ySpeed, xSpeed)
        input.rotate(gyroAngle)

        wheelSpeeds = [
            input.scalarProject(self.leftVec) + zRotation,
            input.scalarProject(self.rightVec) + zRotation,
            input.scalarProject(self.backVec) + zRotation,
        ]

        RobotDriveBase.normalize(wheelSpeeds)

        self.leftMotor.set(wheelSpeeds[0] * self.maxOutput)
        self.rightMotor.set(wheelSpeeds[1] * self.maxOutput)
        self.backMotor.set(wheelSpeeds[2] * self.maxOutput)

        self.feed()

    def drivePolar(self, magnitude: float, angle: float, zRotation: float) -> None:
        """Drive method for Killough platform.

        Angles are measured counter-clockwise from straight ahead. The speed at which the robot
        drives (translation) is independent from its angle or zRotation rate.

        :param magnitude: The robot's speed at a given angle `[-1.0..1.0]`. Forward is positive.
        :param angle: The angle around the Z axis at which the robot drives in degrees `[-180..180]`.
        :param zRotation: The robot's rotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive.
        """
        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                3,
                hal.UsageReporting.kRobotDrive2_KilloughPolar,
            )
            self.reported = True

        magnitude = RobotDriveBase.limit(magnitude) * math.sqrt(2)

        self.driveCartesian(
            magnitude * math.cos(math.radians(angle)),
            magnitude * math.sin(math.radians(angle)),
            zRotation,
            0,
        )

    def stopMotor(self) -> None:
        self.leftMotor.stopMotor()
        self.rightMotor.stopMotor()
        self.backMotor.stopMotor()
        self.feed()

    def getDescription(self) -> str:
        return "Killough Drive"

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("KilloughDrive")
        builder.setActuator(True)
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty(
            "Left Motor Speed", self.leftMotor.get, self.leftMotor.set
        )
        builder.addDoubleProperty(
            "Right Motor Speed", self.rightMotor.get, self.rightMotor.set
        )
        builder.addDoubleProperty(
            "Back Motor Speed", self.backMotor.get, self.backMotor.set
        )
