# validated: 2016-12-01 AA 140c365e4b99 shared/java/edu/wpi/first/wpilibj/JoystickBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .generichid import GenericHID

__all__ = ["JoystickBase"]

class JoystickBase(GenericHID):
    """
    JoystickBase Interface.
    """

    def __init__(self, port):
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

    def getTrigger(self, hand=None):
        """Is the trigger pressed.

        :param hand: which hand
        :returns: true if the trigger for the given hand is pressed
        """

        raise NotImplementedError

    def getTop(self, hand=None):
        """Is the top button pressed.

        :param hand: which hand
        :returns: true if hte top button for the given hand is pressed
        """

        raise NotImplementedError

    def getPOV(self, pov=0):
        raise NotImplementedError

    def getPOVCount(self):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def setOutput(self, outputNumber, value):
        raise NotImplementedError

    def setOutputs(self, value):
        raise NotImplementedError

    def setRumble(self, type, value):
        raise NotImplementedError
