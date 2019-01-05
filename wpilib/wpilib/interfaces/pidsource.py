# validated: 2017-09-24 AA e1195e8b9dab edu/wpi/first/wpilibj/PIDSource.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum
from typing import Callable

__all__ = ["PIDSource"]


class PIDSource:
    """This interface allows for :class:`.PIDController` to automatically read from this
    object.
    """

    @staticmethod
    def from_obj_or_callable(objc: "PIDSource") -> "PIDSource":
        """
            Utility method that gets a PIDSource object
        
            :param objc: An object that implements the PIDSource interface, or
                         a callable
                         
            :returns: an object that implements the PIDSource interface 
        """

        # This isn't pythonic, but will cause errors to happen earlier
        if not hasattr(objc, "pidGet"):
            if not callable(objc):
                raise TypeError("%s must be callable or ")
            return _PIDSourceWrapper(objc)

        if not hasattr(objc, "getPIDSourceType"):
            raise TypeError("%s does not have getPIDSourceType method" % objc)

        return objc

    class PIDSourceType(enum.IntEnum):
        """A description for the type of output value to provide to a
        :class:`.PIDController`"""

        kDisplacement = 0
        kRate = 1

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """Set which parameter of the device you are using as a process control
        variable.
        
        :param pidSource: An enum to select the parameter.
        """
        raise NotImplementedError

    def getPIDSourceType(self) -> PIDSourceType:
        """Get which parameter of the device you are using as a process control
           variable.
           
        :returns: the currently selected PID source parameter
        """
        raise NotImplementedError

    def pidGet(self) -> float:
        """Get the result to use in :class:`.PIDController`
        
        :returns: the result to use in PIDController
        """
        raise NotImplementedError


class _PIDSourceWrapper(PIDSource):
    def __init__(self, fn: Callable) -> None:
        self.pidGet = fn

    def getPIDSourceType(self) -> PIDSource.PIDSourceType:
        return self.PIDSourceType.kDisplacement
