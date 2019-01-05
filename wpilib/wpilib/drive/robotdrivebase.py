# validated: 2018-11-17 EN 665a6e356a14 edu/wpi/first/wpilibj/drive/RobotDriveBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum
from typing import List

from ..motorsafety import MotorSafety
from ..sendablebase import SendableBase

__all__ = ["RobotDriveBase"]


class RobotDriveBase(SendableBase, MotorSafety):
    """Common base class for drive platforms"""

    class MotorType(enum.IntEnum):
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

    kDefaultDeadband = 0.02
    kDefaultMaxOutput = 1.0

    def __init__(self) -> None:
        SendableBase.__init__(self)
        MotorSafety.__init__(self)

        self.deadband = self.kDefaultDeadband
        self.maxOutput = self.kDefaultMaxOutput

        self.setSafetyEnabled(True)
        self.setName("RobotDriveBase")

    def setDeadband(self, deadband: float) -> None:
        """Sets the deadband applied to the drive inputs (e.g. joystick values).

        The default value is :const:`kDefaultDeadband`. Inputs smaller than the deadband are set to
        0 while inputs larger than the deadband are scaled from 0 to 1. See :meth:`applyDeadband`.

        :param deadband: The deadband to set
        """
        self.deadband = deadband

    def setMaxOutput(self, maxOutput: float) -> None:
        """Configure the scaling factor for using drive methods with motor controllers in a mode
        other than PercentVbus or to limit the maximum output.

        The default value is :const:`kDefaultMaxOutput`.

        :param maxOutput: Multiplied with the output percentage computed by the drive functions.
        """
        self.maxOutput = maxOutput

    def feedWatchdog(self):
        """
        Feed the motor safety object. Resets the timer that will stop the 
        motors if it completes.

        see :meth:`.MotorSafety.feed`
        """
        self.feed()

    @staticmethod
    def limit(value: float) -> float:
        """Limit motor values to the -1.0 to +1.0 range."""
        if value > 1.0:
            return 1.0
        if value < -1.0:
            return -1.0
        return value

    @staticmethod
    def applyDeadband(value: float, deadband: float) -> float:
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
    def normalize(wheelSpeeds: List[float]) -> None:
        """Normalize all wheel speeds if the magnitude of any wheel is greater
        than 1.0.

        :param wheelSpeeds: Iterable of wheelspeeds to normalize
        """
        maxMagnitude = max(abs(x) for x in wheelSpeeds)
        if maxMagnitude > 1.0:
            for i in range(len(wheelSpeeds)):
                wheelSpeeds[i] = wheelSpeeds[i] / maxMagnitude
