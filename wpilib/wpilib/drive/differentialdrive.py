# validated: 2017-10-23 TW 19addb04cf4a edu/wpi/first/wpilibj/drive/DifferentialDrive.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import math
from .robotdrivebase import RobotDriveBase

__all__ = ["DifferentialDrive"]


class DifferentialDrive(RobotDriveBase):
    """A class for driving differential drive/skid-steer drive platforms such as the Kit of Parts drive
        base, "tank drive", or West Coast Drive.

        These drive bases typically have drop-center / skid-steer with two or more wheels per side
        (e.g., 6WD or 8WD).

        A differential drive robot has left and right wheels separated by an arbitrary width.

        Drive base diagram:

        |_______|
        | |   | |
          |   |
        |_|___|_|
        |       |


        Each drive() function provides different inverse kinematic relations for a differential drive
        robot. Motor outputs for the right side are negated, so motor direction inversion by the user is
        usually unnecessary.
    """

    def __init__(self, leftMotor, rightMotor):
        """Constructor for DifferentialDrive.

        This class takes in a SpeedController per side. For two and four motor drivetrains
         construct and pass in  :class:`..SpeedControllerGroup` instances as follows.

         :param leftMotor: Left motor SpeedController
         :param rightMotor: Right motor SpeedController
        """
        super().__init__()

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        self.reported = False
        self.quickStopAccumulator = 0.0

    def tankDrive(self, left, right, squaredInputs=True):
        """Provide tank steering using the stored robot configuration.

        :param left: The value to use for the left side motors. [-1.0..1.0]
        :param right: The value to use for the right side motors. [-1.0..1.0]
        :param squaredInputs: If set, decreases the input sensitivity at low speeds
        """

        if not self.reported:
            hal.report(hal.UsageReporting.kResourceType_RobotDrive,
                       2,
                       hal.UsageReporting.kRobotDrive_Tank)
            self.reported = True

        left = RobotDriveBase.limit(left)
        left = RobotDriveBase.applyDeadband(left, self.deadband)

        right = RobotDriveBase.limit(right)
        right = RobotDriveBase.applyDeadband(right, self.deadband)

        # square the inputs (while preserving the sign) to increase fine
        # control while permitting full power
        if squaredInputs:
            left = math.copysign(left * left, left)
            right = math.copysign(right * right, right)

        self.leftMotor.set(left * self.maxOutput)
        self.rightMotor.set(-right * self.maxOutput)

        self.feed()

    def arcadeDrive(self, y, rotation, squaredInputs=True):
        """Provide arcade steering using the stored robot configuration.

        :param y: The value to use for forwards/backwards. [-1.0..1.0]
        :param rotation: The value to use for the rotation right/left. [-1.0..1.0)
        :param squaredInputs: If set, decreases the sensitivity at low speeds.
        """

        if not self.reported:
            hal.report(hal.UsageReporting.kResourceType_RobotDrive,
                       2,
                       hal.UsageReporting.kRobotDrive_ArcadeStandard)
            self.reported = True

        y = RobotDriveBase.limit(y)
        y = RobotDriveBase.applyDeadband(y, self.deadband)

        rotation = RobotDriveBase.limit(rotation)
        rotation = RobotDriveBase.applyDeadband(rotation, self.deadband)

        if squaredInputs:
            # square the inputs (while preserving the sign) to increase fine
            # control while permitting full power
            y = math.copysign(y * y, y)
            rotation = math.copysign(rotation * rotation, rotation)

        maxInput = math.copysign(max(abs(y), abs(rotation)), y)

        if y > 0.0:
            if rotation > 0.0:
                leftMotorSpeed = maxInput
                rightMotorSpeed = y - rotation
            else:
                leftMotorSpeed = y + rotation
                rightMotorSpeed = maxInput
        else:
            if rotation > 0.0:
                leftMotorSpeed = y + rotation
                rightMotorSpeed = maxInput
            else:
                leftMotorSpeed = maxInput
                rightMotorSpeed = y - rotation

        leftMotorSpeed = RobotDriveBase.limit(leftMotorSpeed) * self.maxOutput
        rightMotorSpeed = RobotDriveBase.limit(rightMotorSpeed) * self.maxOutput

        self.leftMotor.set(leftMotorSpeed)
        self.rightMotor.set(rightMotorSpeed)

        self.feed()

    def curvatureDrive(self, y, rotation, isQuickTurn):
        """
        Curvature drive method for differential drive platform.

        The rotation argument controls the curvature of the robot's path rather than its rate
        of heading change. This makes the robot more controllable at high speeds. Also handles
        the robot's quick turn functionality - "quick turn" overrides constant-curvature turning
        for turn-in-place maneuvers

        :param y: The value to use for forwards/backwards. [-1.0..1.0]
        :param rotation:  The value to use for rotation left/right [-1.0..1.0]
        :param isQuickTurn: If set, overrides constant-curvature turning for
                          turn-in-place maneuvers.
        """
        if not self.reported:
            # hal.report(hal.UsageReporting.kResourceType_RobotDrive,
            #           2,
            #           hal.UsageReporting.kRobotDrive_Curvature)
            self.reported = True

        y = RobotDriveBase.limit(y)
        y = RobotDriveBase.applyDeadband(y, self.deadband)

        if isQuickTurn:
            if abs(y) < .2:
                alpha = .1
                self.quickStopAccumulator = (1 - alpha) * self.quickStopAccumulator + alpha * RobotDriveBase.limit(
                    rotation) * 2

            overPower = True
            angularPower = rotation

        else:
            overPower = False
            angularPower = abs(y) * rotation - self.quickStopAccumulator

            if self.quickStopAccumulator > 1:
                self.quickStopAccumulator -= 1
            elif self.quickStopAccumulator < -1:
                self.quickStopAccumulator += 1
            else:
                self.quickStopAccumulator = 0

        leftMotorSpeed = y + angularPower
        rightMotorSpeed = y - angularPower

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

        self.leftMotor.set(leftMotorSpeed * self.maxOutput)
        self.rightMotor.set(rightMotorSpeed * self.maxOutput)

        self.feed()

    def getDescription(self):
        return "Differential Drive"

    def stopMotor(self):
        self.leftMotor.stopMotor()
        self.rightMotor.stopMotor()

        self.feed()
