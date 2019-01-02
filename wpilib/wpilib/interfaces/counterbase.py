# validated: 2017-11-21 EN b65447b6f5a8 edu/wpi/first/wpilibj/CounterBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum

__all__ = ["CounterBase"]


class CounterBase:
    """Interface for counting the number of ticks on a digital input channel.
    Encoders, Gear tooth sensors, and counters should all subclass this so it
    can be used to build more advanced classes for control and driving.

    All counters will immediately start counting - :meth:`reset` them if you
    need them to be zeroed before use.
    """

    class EncodingType(enum.IntEnum):
        """The number of edges for the counterbase to increment or decrement on"""

        #: Count only the rising edge
        k1X = 0

        #: Count both the rising and falling edge
        k2X = 1

        #: Count rising and falling on both channels
        k4X = 2

    def get(self) -> int:
        """Get the count
        
        :returns: the count
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Reset the count to zero"""
        raise NotImplementedError

    def getPeriod(self) -> float:
        """Get the time between the last two edges counted
        
        :returns: the time between the last two ticks in seconds
        """
        raise NotImplementedError

    def setMaxPeriod(self, maxPeriod: float) -> None:
        """Set the maximum time between edges to be considered stalled
        
        :param maxPeriod: the maximum period in seconds
        """
        raise NotImplementedError

    def getStopped(self) -> bool:
        """Determine if the counter is not moving
        
        :returns: True if the counter has not changed for the max period
        """
        raise NotImplementedError

    def getDirection(self) -> bool:
        """Determine which direction the counter is going
        
        :returns: True for one direction, False for the other
        """
        raise NotImplementedError
