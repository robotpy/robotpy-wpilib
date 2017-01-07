# validated: 2016-12-01 AA 140c365e4b99 shared/java/edu/wpi/first/wpilibj/GenericHID.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

__all__ = ["GenericHID"]

class GenericHID:
    """
    GenericHID Interface.
    """

    class RumbleType:
        """Represents a rumble output on the JoyStick."""

        #: Left Hand
        kLeftRumble = 0

        #: Right Hand
        kRightRumble = 1

    class HIDType:
        kUnknown = -1
        kXInputUnknown = 0
        kXInputGamepad = 1
        kXInputWheel = 2
        kXInputArcadeStick = 3
        kXInputFlightStick = 4
        kXInputDancePad = 5
        kXInputGuitar = 6
        kXInputGuitar2 = 7
        kXInputDrumKit = 8
        kXInputGuitar3 = 11
        kXInputArcadePad = 19
        kHIDJoystick = 20
        kHIDGamepad = 21
        kHIDDriving = 22
        kHIDFlight = 23
        kHID1stPerson = 24

        def __init__(self, value):
            self.value = value

    class Hand:
        """Which hand the Human Interface Device is associated with."""

        #: Left Hand
        kLeft = 0

        #: Right Hand
        kRight = 1

    def __init__(self, port):
        self.port = port

    def getX(self, hand=None):
        """Get the x position of HID.

        :param hand: which hand, left or right
        :returns: the x position
        """
        raise NotImplementedError

    def getY(self, hand=None):
        """Get the y position of the HID.

        :param hand: which hand, left or right
        :returns: the y position
        """
        raise NotImplementedError

    def getRawAxis(self, which):
        """Get the raw axis.

        :param which: index of the axis
        :returns: the raw value of the selected axis
        """
        raise NotImplementedError

    def getRawButton(self, button):
        """Is the given button pressed.

        :param button: which button number
        :returns: the angle of the POV in degrees, or -1 if the POV is not pressed.
        """
        raise NotImplementedError

    def getPOV(self, pov=0):
        """Get the angle in degrees of a POV on the HID.

        The POV angles start at 0 in the up direction, and increase clockwise (eg right is 90,
        upper-left is 315).

        :param pov: The index of the POV to read (starting at 0)
        :returns: the angle of the POV in degrees, or -1 if the POV is not pressed.
        """
        raise NotImplementedError

    def getPOVCount(self):
        """For the current HID, return the number of POVs."""
        pass

    def getPort(self):
        """Get the port number of the HID.

        :returns: The port number of the HID.
        """
        return self.port

    def getType(self):
        """Get the type of the HID.

        :returns: the type of the HID.
        """
        raise NotImplementedError

    def getName(self):
        """Get the name of the HID.

        :returns: the name of the HID.
        """
        raise NotImplementedError

    def setOutput(self, outputNumber, value):
        """Set a single HID output value for the HID.

        :param outputNumber: The index of the output to set (1-32)
        :param value: The value to set the output to
        """
        raise NotImplementedError

    def setOutputs(self, value):
        """Set all HID output values for the HID.

        :param value: The 32 bit output value (1 bit for each output)
        """
        raise NotImplementedError

    def setRumble(self, type, value):
        """Set the rumble output for the HID. The DS currently supports 2 rumble values, left rumble and
        right rumble.

        :param type: Which rumble value to set
        :param value: The normalized value (0 to 1) to set the rumble to
        """
        raise NotImplementedError
