# validated: 2017-09-27 AA e1195e8b9dab edu/wpi/first/wpilibj/interfaces/Accelerometer.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in $(WIND_BASE)/WPILib.
# ----------------------------------------------------------------------------
import enum

__all__ = ["Accelerometer"]


class Accelerometer:
    """Interface for 3-axis accelerometers"""

    class Range(enum.IntEnum):
        k2G = 0
        k4G = 1
        k8G = 2
        k16G = 3

    def setRange(self, range: Range) -> None:
        """Common interface for setting the measuring range of an
        accelerometer.

        :param range: The maximum acceleration, positive or negative, that
                      the accelerometer will measure.  Not all accelerometers
                      support all ranges.
        """
        raise NotImplementedError

    def getX(self) -> float:
        """Common interface for getting the x axis acceleration

        :returns: The acceleration along the x axis in g-forces
        """
        raise NotImplementedError

    def getY(self) -> float:
        """Common interface for getting the y axis acceleration

        :returns: The acceleration along the y axis in g-forces
        """
        raise NotImplementedError

    def getZ(self) -> float:
        """Common interface for getting the z axis acceleration

        :returns: The acceleration along the z axis in g-forces
        """
        raise NotImplementedError
