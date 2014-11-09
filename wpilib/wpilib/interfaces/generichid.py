#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

__all__ = ["GenericHID"]

class GenericHID:
    """GenericHID Interface"""

    class Hand:
        """Which hand the Human Interface Device is associated with."""
        
        #: Left hand
        kLeft = 0
        
        #: Right hand
        kRight = 1

    def getX(self, hand=None):
        """Get the x position of HID.

        :param hand: which hand, left or right (default right)
        :returns: the x position
        """
        raise NotImplementedError

    def getY(self, hand=None):
        """Get the y position of the HID.

        :param hand: which hand, left or right (default right)
        :returns: the y position
        """
        raise NotImplementedError

    def getZ(self, hand=None):
        """Get the z position of the HID.

        :param hand: which hand, left or right (default right)
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

    def getRawAxis(self, which):
        """Get the raw axis.

        :param which: index of the axis
        :returns: the raw value of the selected axis
        """
        raise NotImplementedError

    def getTrigger(self, hand=None):
        """Is the trigger pressed
        
        :param hand: which hand (default right)
        :returns: True if the trigger for the given hand is pressed
        """
        raise NotImplementedError

    def getTop(self, hand=None):
        """Is the top button pressed
        
        :param hand: which hand (default right)
        :returns: True if the top button for the given hand is pressed
        """
        raise NotImplementedError

    def getBumper(self, hand=None):
        """Is the bumper pressed?

        :param hand: which hand (default right)
        :returns: True if the bumper is pressed
        """
        raise NotImplementedError

    def getRawButton(self, button):
        """Is the given button pressed?

        :param button: which button number
        :returns: True if the button is pressed
        """
        raise NotImplementedError

    def getPOV(self, pov=0):
        """Get the state of a POV.

        :param pov: which POV (default is 0)
        :returns: The angle of the POV in degrees, or -1 if the POV is not
                  pressed.
        """
        raise NotImplementedError
