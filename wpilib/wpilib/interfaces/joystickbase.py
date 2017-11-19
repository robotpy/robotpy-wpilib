# validated: 2017-11-13 TW 21585f70a88e edu/wpi/first/wpilibj/JoystickBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------
import warnings

from .generichid import GenericHID

__all__ = ["JoystickBase"]

class JoystickBase(GenericHID):
    """
    JoystickBase Interface.

    ..deprecated:: 2018.0.0
        Inherit directly from GenericHID instead.
    """

    def __init__(self, port):
        warnings.warn("JoystickBase is deprecated. Inherit directly from GenericHID instead", DeprecationWarning, stacklevel=2)
        super().__init__(port)

    def getZ(self, hand=None):
        """Get the z position of the HID.

        :param hand: which hand, left or right
        :returns: the z position
        """

        raise NotImplementedError

    def getTwist(self):
        """Get the twist value.

        :returns: the twist value
        """

        raise NotImplementedError

    def getThrottle(self):
        """Get the throttle.

        :returns: the throttle value
        """

        raise NotImplementedError
