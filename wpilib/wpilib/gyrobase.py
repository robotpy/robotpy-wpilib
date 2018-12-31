# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/GyroBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .interfaces import PIDSource
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

__all__ = ["GyroBase"]


class GyroBase(SendableBase):
    """
        GyroBase is the common base class for Gyro implementations such as
        :class:`.AnalogGyro`.
    """

    PIDSourceType = PIDSource.PIDSourceType

    def __init__(self) -> None:
        super().__init__()
        self.pidSource = self.PIDSourceType.kDisplacement
        self.valueEntry = None

    def calibrate(self) -> None:
        raise NotImplementedError()

    def reset(self) -> None:
        raise NotImplementedError()

    def getAngle(self) -> float:
        raise NotImplementedError()

    def getRate(self) -> float:
        raise NotImplementedError()

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """Set which parameter of the gyro you are using as a process
        control variable. The Gyro class supports the rate and angle
        parameters.

        :param pidSource: An enum to select the parameter.
        """
        if pidSource not in (
            self.PIDSourceType.kDisplacement,
            self.PIDSourceType.kRate,
        ):
            raise ValueError("Must be kRate or kDisplacement")
        self.pidSource = pidSource

    def getPIDSourceType(self) -> PIDSourceType:
        return self.pidSource

    def pidGet(self) -> float:
        """Get the output of the gyro for use with PIDControllers. May be
        the angle or rate depending on the set :class:`.PIDSourceType`

        :returns: the current angle according to the gyro
        """
        if self.pidSource == self.PIDSourceType.kRate:
            return self.getRate()
        elif self.pidSource == self.PIDSourceType.kDisplacement:
            return self.getAngle()
        else:
            return 0.0

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Gyro")
        builder.addDoubleProperty("Value", self.getAngle, None)
