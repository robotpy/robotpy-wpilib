# validated: 2019-01-06 TW a60f312d19ee edu/wpi/first/wpilibj/drive/MecanumDrive.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
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

__all__ = ["MecanumDrive"]


class MecanumDrive(RobotDriveBase):
    r"""A class for driving Mecanum drive platforms.

    Mecanum drives are rectangular with one wheel on each corner. Each wheel has rollers toed in
    45 degrees toward the front or back. When looking at the wheels from the top, the roller axles
    should form an X across the robot. Each drive() function provides different inverse kinematic
    relations for a Mecanum drive robot.

    Drive base diagram::

        \_______/
        \ |   | /
          |   |
        /_|___|_\
        /       \


    Each drive() function provides different inverse kinematic relations for a Mecanum drive
    robot. Motor outputs for the right side are negated, so motor direction inversion by the user is
    usually unnecessary.

    This library uses the NED axes convention (North-East-Down as external reference in the world
    frame): http://www.nuclearprojects.com/ins/images/axis_big.png.

    The positive X axis points ahead, the positive Y axis points right, and the positive Z axis
    points down. Rotations follow the right-hand rule, so clockwise rotation around the Z axis is
    positive.

    .. note:: RobotDrive porting guide:

        In MecanumDrive, the right side speed controllers are automatically inverted,
        while in RobotDrive, no speed controllers are automatically inverted.

        :meth:`driveCartesian` is equivalent to :meth:`.RobotDrive.mecanumDrive_Cartesian` if a deadband of 0
        is used, and the ``ySpeed`` and ``gyroAngle`` values are inverted compared to ``RobotDrive`` (i.e
        ``driveCartesian(xSpeed, -ySpeed, zRotation, -gyroAngle)``.

        :meth:`drivePolar` is equivalent to :meth:`.RobotDrive.mecanumPolar` if a deadband of 0 is used.
    """

    instances = 0

    def __init__(
        self,
        frontLeftMotor: SpeedController,
        rearLeftMotor: SpeedController,
        frontRightMotor: SpeedController,
        rearRightMotor: SpeedController,
    ) -> None:
        """Constructor for MecanumDrive.

        If motors need to be inverted, do so beforehand.
        Motor outputs for the right side are negated, so motor direction inversion
        by the user is usually unnecessary

        :param frontLeftMotor: Front Left Motor
        :param rearLeftMotor: Rear Left Motor
        :param frontRightMotor: Front Right Motor
        :param rearRightMotor: Rear Right Motor
        """
        assert frontLeftMotor is not None, "Front Left Motor should not be None"
        assert rearLeftMotor is not None, "Rear Left Motor should not be None"
        assert frontRightMotor is not None, "Front Right Motor should not be None"
        assert rearRightMotor is not None, "Rear Right Motor should not be None"
        super().__init__()

        self.frontLeftMotor = frontLeftMotor
        self.rearLeftMotor = rearLeftMotor
        self.frontRightMotor = frontRightMotor
        self.rearRightMotor = rearRightMotor

        self.addChild(self.frontLeftMotor)
        self.addChild(self.rearLeftMotor)
        self.addChild(self.frontRightMotor)
        self.addChild(self.rearRightMotor)
        MecanumDrive.instances += 1
        self.setName("MecanumDrive", self.instances)

        self.rightSideInvertMultiplier = -1.0
        self.reported = False

    def driveCartesian(
        self, ySpeed: float, xSpeed: float, zRotation: float, gyroAngle: float = 0.0
    ) -> None:
        """Drive method for Mecanum platform.

        Angles are measured clockwise from the positive X axis. The robot's speed is independent
        from its angle or rotation rate.

        :param ySpeed: The robot's speed along the Y axis [-1.0..1.0]. Right is positive.
        :param xSpeed: The robot's speed along the X axis [-1.0..1.0]. Forward is positive.
        :param zRotation: The robot's rotation rate around the Z axis [-1.0..1.0]. Clockwise is positive.
        :param gyroAngle: The current angle reading from the gyro in degrees around the Z axis. Use
                          this to implement field-oriented controls.
        """
        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                4,
                hal.UsageReporting.kRobotDrive2_MecanumCartesian,
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
            # Front Left
            input.x + input.y + zRotation,
            # Rear Left
            -input.x + input.y + zRotation,
            # Front Right
            -input.x + input.y - zRotation,
            # Rear Right
            input.x + input.y - zRotation,
        ]

        RobotDriveBase.normalize(wheelSpeeds)

        wheelSpeeds = [speed * self.maxOutput for speed in wheelSpeeds]

        self.frontLeftMotor.set(wheelSpeeds[0])
        self.rearLeftMotor.set(wheelSpeeds[1])
        self.frontRightMotor.set(wheelSpeeds[2] * self.rightSideInvertMultiplier)
        self.rearRightMotor.set(wheelSpeeds[3] * self.rightSideInvertMultiplier)

        self.feed()

    def drivePolar(self, magnitude: float, angle: float, zRotation: float) -> None:
        """Drive method for Mecanum platform.

        Angles are measured counter-clockwise from straight ahead. The speed at which the robot
        drives (translation) is independent from its angle or rotation rate.

        :param magnitude: The robot's speed at a given angle [-1.0..1.0]. Forward is positive.
        :param angle: The angle around the Z axis at which the robot drives in degrees [-180..180].
        :param zRotation: The robot's rotation rate around the Z axis [-1.0..1.0]. Clockwise is
                          positive.
        """
        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                4,
                hal.UsageReporting.kRobotDrive2_MecanumPolar,
            )
            self.reported = True

        magnitude = RobotDriveBase.limit(magnitude) * math.sqrt(2)

        self.driveCartesian(
            magnitude * math.cos(math.radians(angle)),
            magnitude * math.sin(math.radians(angle)),
            zRotation,
            0.0,
        )

    def isRightSideInverted(self):
        """
        Gets if the power sent to the right side of the drivetrain is
        multipled by -1.

        :returns: true if the right side is inverted
        """
        return self.rightSideInvertMultiplier == -1.0

    def setRightSideInverted(self, rightSideInverted: bool) -> None:
        """
        Sets if the power sent to the right side of the drivetrain should
        be multipled by -1.

        :param rightSideInverted: true if right side power should be multipled
                                  by -1
        """
        self.rightSideInvertMultiplier = -1.0 if rightSideInverted else 1.0

    def stopMotor(self) -> None:
        self.frontLeftMotor.stopMotor()
        self.rearLeftMotor.stopMotor()
        self.frontRightMotor.stopMotor()
        self.rearRightMotor.stopMotor()
        self.feed()

    def getDescription(self) -> str:
        return "Mecanum Drive"

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("MecanumDrive")
        builder.setActuator(True)
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty(
            "Front Left Motor Speed", self.frontLeftMotor.get, self.frontLeftMotor.set
        )
        builder.addDoubleProperty(
            "Front Right Motor Speed",
            lambda: self.frontRightMotor.get() * self.rightSideInvertMultiplier,
            lambda v: self.frontRightMotor.set(v * self.rightSideInvertMultiplier),
        )
        builder.addDoubleProperty(
            "Rear Left Motor Speed", self.rearLeftMotor.get, self.rearLeftMotor.set
        )
        builder.addDoubleProperty(
            "Rear Right Motor Speed",
            lambda: self.rearRightMotor.get() * self.rightSideInvertMultiplier,
            lambda v: self.rearRightMotor.set(v * self.rightSideInvertMultiplier),
        )
