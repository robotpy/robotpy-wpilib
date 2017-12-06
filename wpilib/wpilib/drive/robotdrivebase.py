# validated: 2017-10-23 TW 19addb04cf4a edu/wpi/first/wpilibj/drive/RobotDriveBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from ..motorsafety import MotorSafety

__all__ = ["RobotDriveBase"]


class RobotDriveBase(MotorSafety):
    """Common base class for drive platforms"""

    class MotorType:
        """The location of a motor on the robot for the purpose of driving."""

        #: Front left
        kFrontLeft = 0

        #: Front right
        kFrontRight = 1

        #: Rear left
        kRearLeft = 2

        #: Rear right
        kRearRight = 3

        #: Left
        kLeft = 0

        #: Right
        kRight = 1

        #: Back
        kBack = 2

    maxOutput = 1.0
    deadband = .02

    def __init__(self):
        super().__init__()

    def setDeadband(self, deadband):
        self.deadband = deadband

    def setMaxOutput(self, maxOutput):
        """Configure the scaling factor for using RobotDrive with motor controllers in a mode other than PercentVbus.

        :param maxOutput: Multiplied with the output percentage computed by the drive functions.
        """
        self.maxOutput = maxOutput

    @staticmethod
    def limit(value):
        """Limit motor values to the -1.0 to +1.0 range."""
        if value > 1.0:
            return 1.0
        if value < -1.0:
            return -1.0
        return value

    @staticmethod
    def applyDeadband(value, deadband):
        """Returns 0.0 if the given value is within the specified range around zero. The remaining range
        between the deadband and 1.0 is scaled from 0.0 to 1.0.

        :param value: value to clip
        :param deadband: range around zero
        """
        if abs(value) > deadband:
            if value < 0.0:
                return (value - deadband) / (1.0 - deadband)
            else:
                return (value + deadband) / (1.0 - deadband)
        return 0.0

    @staticmethod
    def normalize(wheelSpeeds):
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1.0.

        :param wheelSpeeds: Iterable of wheelspeeds to normalize
        """
        maxMagnitude = max(abs(x) for x in wheelSpeeds)
        if maxMagnitude > 1.0:
            for i in range(len(wheelSpeeds)):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude
