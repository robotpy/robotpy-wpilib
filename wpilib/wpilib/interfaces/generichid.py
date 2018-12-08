# validated: 2018-11-17 EN e7cf6bf7c58b edu/wpi/first/wpilibj/GenericHID.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum

from ..driverstation import DriverStation
import hal

__all__ = ["GenericHID"]


class GenericHID:
    """
    GenericHID Interface.
    """

    class RumbleType(enum.IntEnum):
        """Represents a rumble output on the JoyStick."""

        #: Left Hand
        kLeftRumble = 0

        #: Right Hand
        kRightRumble = 1

    class HIDType(enum.IntEnum):
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

    class Hand(enum.IntEnum):
        """Which hand the Human Interface Device is associated with."""

        #: Left Hand
        kLeft = 0

        #: Right Hand
        kRight = 1

    def __init__(self, port: int) -> None:
        self.port = port
        self.ds = DriverStation.getInstance()
        self.outputs = 0
        self.leftRumble = 0
        self.rightRumble = 0

    def getX(self, hand: Hand = Hand.kRight) -> float:
        """Get the x position of HID.

        :param hand: which hand, left or right
        :returns: the x position
        """
        raise NotImplementedError

    def getY(self, hand: Hand = Hand.kRight) -> float:
        """Get the y position of the HID.

        :param hand: which hand, left or right
        :returns: the y position
        """
        raise NotImplementedError

    def getRawButton(self, button: int) -> bool:
        """Get the button value (starting at button 1).

        :param button: The button number to be read (starting at 1)
        :returns: The state of the button.
        """
        return self.ds.getStickButton(self.port, button)

    def getRawButtonPressed(self, button: int) -> bool:
        """Whether the button was pressed since the last check. Button indexes begin at 1.

        :param button: The button index, beginning at 1.
        :returns: Whether the button was pressed since the last check.

        .. versionadded:: 2018.0.0
        """
        return self.ds.getStickButtonPressed(self.port, button)

    def getRawButtonReleased(self, button: int) -> bool:
        """Whether the button was released since the last check. Button indexes begin at 1.

        :param button: The button index, beginning at 1.
        :returns: Whether the button was released since the last check.

        .. versionadded:: 2018.0.0
        """
        return self.ds.getStickButtonReleased(self.port, button)

    def getRawAxis(self, axis: int) -> float:
        """Get the raw axis.

        :param axis: index of the axis
        :returns: the raw value of the selected axis
        """
        return self.ds.getStickAxis(self.port, axis)

    def getPOV(self, pov: int = 0) -> int:
        """Get the angle in degrees of a POV on the HID.

        The POV angles start at 0 in the up direction, and increase clockwise (eg right is 90,
        upper-left is 315).

        :param pov: The index of the POV to read (starting at 0)
        :returns: the angle of the POV in degrees, or -1 if the POV is not pressed.
        """
        return self.ds.getStickPOV(self.port, pov)

    def getAxisCount(self) -> int:
        """Get the number of axes for the HID

        :returns: The number of axis for the current HID
        """
        return self.ds.getStickAxisCount(self.port)

    def getPOVCount(self) -> int:
        """For the current HID, return the number of POVs."""
        return self.ds.getStickPOVCount(self.port)

    def getButtonCount(self) -> int:
        """For the current HID, return the number of buttons."""
        return self.ds.getStickButtonCount(self.port)

    def getPort(self) -> int:
        """Get the port number of the HID.

        :returns: The port number of the HID.
        """
        return self.port

    def getType(self) -> HIDType:
        """Get the type of the HID.

        :returns: the type of the HID.
        """
        return self.HIDType(self.ds.getJoystickType(self.port))

    def getName(self) -> str:
        """Get the name of the HID.

        :returns: the name of the HID.
        """
        return self.ds.getJoystickName(self.port)

    def setOutput(self, outputNumber: int, value: bool) -> None:
        """Set a single HID output value for the HID.

        :param outputNumber: The index of the output to set (1-32)
        :param value: The value to set the output to
        """
        self.outputs = (self.outputs & ~(1 << (outputNumber - 1))) | (
            (1 if value else 0) << (outputNumber - 1)
        )
        hal.setJoystickOutputs(
            self.port, self.outputs, self.leftRumble, self.rightRumble
        )

    def setOutputs(self, value: int) -> None:
        """Set all HID output values for the HID.

        :param value: The 32 bit output value (1 bit for each output)
        """
        self.outputs = value
        hal.setJoystickOutputs(
            self.port, self.outputs, self.leftRumble, self.rightRumble
        )

    def setRumble(self, type: RumbleType, value: float) -> None:
        """Set the rumble output for the HID. The DS currently supports 2 rumble values, left rumble and
        right rumble.

        :param type: Which rumble value to set
        :param value: The normalized value (0 to 1) to set the rumble to
        """
        if value < 0:
            value = 0
        elif value > 1:
            value = 1

        if type == self.RumbleType.kLeftRumble:
            self.leftRumble = int(value * 65535)
        else:
            self.rightRumble = int(value * 65535)

        hal.setJoystickOutputs(
            self.port, self.outputs, self.leftRumble, self.rightRumble
        )
