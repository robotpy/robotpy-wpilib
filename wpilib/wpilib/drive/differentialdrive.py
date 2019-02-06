# validated: 2019-01-06 TW a60f312d19ee edu/wpi/first/wpilibj/drive/DifferentialDrive.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2018. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import math

import hal

from .robotdrivebase import RobotDriveBase
from ..sendablebuilder import SendableBuilder
from ..interfaces.speedcontroller import SpeedController

__all__ = ["DifferentialDrive"]


class DifferentialDrive(RobotDriveBase):
    """
    A class for driving differential drive/skid-steer drive platforms such as the Kit of Parts drive
    base, "tank drive", or West Coast Drive.

    These drive bases typically have drop-center / skid-steer with two or more wheels per side
    (e.g., 6WD or 8WD).

    This class takes a :class:`.SpeedController` per side. For four and six motor
    drivetrains, construct and pass in :class:`.SpeedControllerGroup` instances as follows.

    Four motor drivetrain::

        def robotInit(self):
            self.frontLeft = wpilib.Spark(1)
            self.rearLeft = wpilib.Spark(2)
            self.left = wpilib.SpeedControllerGroup(self.frontLeft, self.rearLeft)

            self.frontRight = wpilib.Spark(3)
            self.rearRight = wpilib.Spark(4)
            self.right = wpilib.SpeedControllerGroup(self.frontRight, self.rearRight)

            self.drive = DifferentialDrive(self.left, self.right)

    Six motor drivetrain::

        def robotInit(self):
            self.frontLeft = wpilib.Spark(1)
            self.midLeft = wpilib.Spark(2)
            self.rearLeft = wpilib.Spark(3)
            self.left = wpilib.SpeedControllerGroup(self.frontLeft, self.midLeft, self.rearLeft)

            self.frontRight = wpilib.Spark(4)
            self.midRight = wpilib.Spark(5)
            self.rearRight = wpilib.Spark(6)
            self.right = wpilib.SpeedControllerGroup(self.frontRight, self.midRight, self.rearRight)

            self.drive = DifferentialDrive(self.left, self.right)

    A differential drive robot has left and right wheels separated by an arbitrary width.

    Drive base diagram::

        |_______|
        | |   | |
          |   |
        |_|___|_|
        |       |


    Each ``drive()`` function provides different inverse kinematic relations for a differential drive
    robot. Motor outputs for the right side are negated, so motor direction inversion by the user is
    usually unnecessary.

    This library uses the NED axes convention (North-East-Down as external reference in the world
    frame): http://www.nuclearprojects.com/ins/images/axis_big.png.

    The positive X axis points ahead, the positive Y axis points right, and the positive Z axis
    points down. Rotations follow the right-hand rule, so clockwise rotation around the Z axis is
    positive.

    Inputs smaller than :data:`.RobotDriveBase.kDefaultDeadband` will be set to
    0, and larger values will be scaled so that the full range is still used.
    This deadband value can be changed with :meth:`~.RobotDriveBase.setDeadband`.

    .. note:: RobotDrive porting guide:

        :meth:`.tankDrive` is equivalent to
        :meth:`.RobotDrive.tankDrive` if a deadband of 0 is used.

        :meth:`.arcadeDrive` is equivalent to
        :meth:`.RobotDrive.arcadeDrive` if a deadband of 0 is used
        and the rotation input is inverted (i.e ``arcadeDrive(y, -rotation)``)

        :meth:`.curvatureDrive` is similar in concept to
        :meth:`.RobotDrive.drive` with the addition of a quick turn
        mode. However, it is not designed to give exactly the same response.
    """

    kDefaultQuickStopThreshold = 0.2
    kDefaultQuickStopAlpha = 0.1

    instances = 0

    def __init__(self, leftMotor: SpeedController, rightMotor: SpeedController) -> None:
        """Constructor for DifferentialDrive.

        .. note:: To pass multiple motors per side, use a :class:`.SpeedControllerGroup`.
                  If a motor needs to be inverted, do so before passing it in.

        :param leftMotor: Left motor(s)
        :param rightMotor: Right motor(s)
        """
        assert leftMotor is not None, "Left Motor should not be None"
        assert rightMotor is not None, "Right Motor should not be None"
        super().__init__()

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        self.quickStopThreshold = self.kDefaultQuickStopThreshold
        self.quickStopAlpha = self.kDefaultQuickStopAlpha
        self.quickStopAccumulator = 0.0
        self.reported = False
        self.rightSideInvertMultiplier = -1.0

        self.addChild(self.leftMotor)
        self.addChild(self.rightMotor)
        DifferentialDrive.instances += 1
        self.setName("DifferentialDrive", self.instances)

    def arcadeDrive(
        self, xSpeed: float, zRotation: float, squareInputs: bool = True
    ) -> None:
        """Arcade drive method for differential drive platform.

        :param xSpeed: The robot's speed along the X axis `[-1.0..1.0]`. Forward is positive
        :param zRotation: The robot's zRotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive
        :param squareInputs: If set, decreases the sensitivity at low speeds.
        """

        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                2,
                hal.UsageReporting.kRobotDrive_ArcadeStandard,
            )
            self.reported = True

        xSpeed = RobotDriveBase.limit(xSpeed)
        xSpeed = RobotDriveBase.applyDeadband(xSpeed, self.deadband)

        zRotation = RobotDriveBase.limit(zRotation)
        zRotation = RobotDriveBase.applyDeadband(zRotation, self.deadband)

        if squareInputs:
            # Square the inputs (while preserving the sign) to increase fine
            # control while permitting full power.
            xSpeed = math.copysign(xSpeed * xSpeed, xSpeed)
            zRotation = math.copysign(zRotation * zRotation, zRotation)

        maxInput = math.copysign(max(abs(xSpeed), abs(zRotation)), xSpeed)

        if xSpeed >= 0.0:
            if zRotation >= 0.0:
                leftMotorSpeed = maxInput
                rightMotorSpeed = xSpeed - zRotation
            else:
                leftMotorSpeed = xSpeed + zRotation
                rightMotorSpeed = maxInput
        else:
            if zRotation >= 0.0:
                leftMotorSpeed = xSpeed + zRotation
                rightMotorSpeed = maxInput
            else:
                leftMotorSpeed = maxInput
                rightMotorSpeed = xSpeed - zRotation

        leftMotorSpeed = RobotDriveBase.limit(leftMotorSpeed) * self.maxOutput
        rightMotorSpeed = RobotDriveBase.limit(rightMotorSpeed) * self.maxOutput

        self.leftMotor.set(leftMotorSpeed)
        self.rightMotor.set(rightMotorSpeed * self.rightSideInvertMultiplier)

        self.feed()

    def curvatureDrive(
        self, xSpeed: float, zRotation: float, isQuickTurn: bool
    ) -> None:
        """
        Curvature drive method for differential drive platform.

        The zRotation argument controls the curvature of the robot's path rather than its rate
        of heading change. This makes the robot more controllable at high speeds. Also handles
        the robot's quick turn functionality - "quick turn" overrides constant-curvature turning
        for turn-in-place maneuvers

        :param xSpeed: The robot's speed along the X axis `[-1.0..1.0]`. Forward is positive.
        :param zRotation:  The robot's rotation rate around the Z axis `[-1.0..1.0]`. Clockwise is positive.
        :param isQuickTurn: If set, overrides constant-curvature turning for
                          turn-in-place maneuvers.
        """
        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                2,
                hal.UsageReporting.kRobotDrive2_DifferentialCurvature,
            )
            self.reported = True

        xSpeed = RobotDriveBase.limit(xSpeed)
        xSpeed = RobotDriveBase.applyDeadband(xSpeed, self.deadband)

        zRotation = RobotDriveBase.limit(zRotation)
        zRotation = RobotDriveBase.applyDeadband(zRotation, self.deadband)

        if isQuickTurn:
            if abs(xSpeed) < self.quickStopThreshold:
                self.quickStopAccumulator = (
                    (1 - self.quickStopAlpha) * self.quickStopAccumulator
                    + self.quickStopAlpha * RobotDriveBase.limit(zRotation) * 2
                )

            overPower = True
            angularPower = zRotation

        else:
            overPower = False
            angularPower = abs(xSpeed) * zRotation - self.quickStopAccumulator

            if self.quickStopAccumulator > 1:
                self.quickStopAccumulator -= 1
            elif self.quickStopAccumulator < -1:
                self.quickStopAccumulator += 1
            else:
                self.quickStopAccumulator = 0

        leftMotorSpeed = xSpeed + angularPower
        rightMotorSpeed = xSpeed - angularPower

        if overPower:
            if leftMotorSpeed > 1.0:
                rightMotorSpeed -= leftMotorSpeed - 1.0
                leftMotorSpeed = 1.0
            elif rightMotorSpeed > 1.0:
                leftMotorSpeed -= rightMotorSpeed - 1.0
                rightMotorSpeed = 1.0
            elif leftMotorSpeed < -1.0:
                rightMotorSpeed -= leftMotorSpeed + 1.0
                leftMotorSpeed = -1.0
            elif rightMotorSpeed < -1.0:
                leftMotorSpeed -= rightMotorSpeed + 1.0
                rightMotorSpeed = -1.0

        # Normalize the wheel speeds
        maxMagnitude = max(abs(leftMotorSpeed), abs(rightMotorSpeed))
        if maxMagnitude > 1.0:
            leftMotorSpeed /= maxMagnitude
            rightMotorSpeed /= maxMagnitude

        self.leftMotor.set(leftMotorSpeed * self.maxOutput)
        self.rightMotor.set(
            rightMotorSpeed * self.maxOutput * self.rightSideInvertMultiplier
        )

        self.feed()

    def tankDrive(
        self, leftSpeed: float, rightSpeed: float, squareInputs: bool = True
    ) -> None:
        """Provide tank steering using the stored robot configuration.

        :param leftSpeed: The robot's left side speed along the X axis `[-1.0..1.0]`. Forward is positive.
        :param rightSpeed: The robot's right side speed along the X axis`[-1.0..1.0]`. Forward is positive.
        :param squareInputs: If set, decreases the input sensitivity at low speeds
        """

        if not self.reported:
            hal.report(
                hal.UsageReporting.kResourceType_RobotDrive,
                2,
                hal.UsageReporting.kRobotDrive2_DifferentialTank,
            )
            self.reported = True

        leftSpeed = RobotDriveBase.limit(leftSpeed)
        leftSpeed = RobotDriveBase.applyDeadband(leftSpeed, self.deadband)

        rightSpeed = RobotDriveBase.limit(rightSpeed)
        rightSpeed = RobotDriveBase.applyDeadband(rightSpeed, self.deadband)

        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        if squareInputs:
            leftSpeed = math.copysign(leftSpeed * leftSpeed, leftSpeed)
            rightSpeed = math.copysign(rightSpeed * rightSpeed, rightSpeed)

        self.leftMotor.set(leftSpeed * self.maxOutput)
        self.rightMotor.set(
            rightSpeed * self.maxOutput * self.rightSideInvertMultiplier
        )

        self.feed()

    def setQuickStopThreshold(self, threshold: float) -> None:
        """Sets the QuickStop speed threshold in curvature drive.

        QuickStop compensates for the robot's moment of inertia when stopping after a QuickTurn.

        While QuickTurn is enabled, the QuickStop accumulator takes on the rotation rate value
        outputted by the low-pass filter when the robot's speed along the X axis is below the
        threshold. When QuickTurn is disabled, the accumulator's value is applied against the computed
        angular power request to slow the robot's rotation.

        :param threshold: X speed below which quick stop accumulator will receive rotation rate values `[0..1.0]`.
        """
        self.quickStopThreshold = threshold

    def setQuickStopAlpha(self, alpha: float) -> None:
        """Sets the low-pass filter gain for QuickStop in curvature drive.

        The low-pass filter filters incoming rotation rate commands to smooth out high frequency
        changes.

        :param alpha: Low-pass filter gain [0.0..2.0]. Smaller values result in slower output changes.
                      Values between 1.0 and 2.0 result in output oscillation. Values below 0.0 and
                      above 2.0 are unstable.
        """
        self.quickStopAlpha = alpha

    def isRightSideInverted(self) -> bool:
        """
        Gets if the power sent to the right side of the drivetrain is multipled by -1.

        :returns: true if the right side is inverted
        """
        return self.rightSideInvertMultiplier == -1.0

    def setRightSideInverted(self, rightSideInverted: bool) -> None:
        """
        Sets if the power sent to the right side of the drivetrain should be multipled by -1.

        :param rightSideInverted: true if right side power should be multipled by -1
        """
        self.rightSideInvertMultiplier = -1.0 if rightSideInverted else 1.0

    def stopMotor(self) -> None:
        self.leftMotor.stopMotor()
        self.rightMotor.stopMotor()

        self.feed()

    def getDescription(self) -> str:
        return "Differential Drive"

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("DifferentialDrive")
        builder.setActuator(True)
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty(
            "Left Motor Speed", self.leftMotor.get, self.leftMotor.set
        )
        builder.addDoubleProperty(
            "Right Motor Speed",
            lambda: self.rightMotor.get() * self.rightSideInvertMultiplier,
            lambda x: self.rightMotor.set(x * self.rightSideInvertMultiplier),
        )
