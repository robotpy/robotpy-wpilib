# validated: 2018-09-30 EN 64b03704f8db edu/wpi/first/wpilibj/Joystick.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum
import math
import warnings

import hal
from .interfaces.generichid import GenericHID

__all__ = ["Joystick"]


class Joystick(GenericHID):
    """Handle input from standard Joysticks connected to the Driver Station.
    
    This class handles standard input that comes from the Driver Station. Each
    time a value is requested the most recent value is returned. There is a
    single class instance for each joystick and the mapping of ports to
    hardware buttons depends on the code in the Driver Station.
    """

    kDefaultXChannel = 0
    kDefaultYChannel = 1
    kDefaultZChannel = 2
    kDefaultTwistChannel = 2
    kDefaultThrottleChannel = 3

    kDefaultXAxis = 0
    kDefaultYAxis = 1
    kDefaultZAxis = 2
    kDefaultTwistAxis = 2
    kDefaultThrottleAxis = 3
    kDefaultTriggerButton = 1
    kDefaultTopButton = 2

    class AxisType(enum.IntEnum):
        """Represents an analog axis on a joystick."""

        kX = 0
        kY = 1
        kZ = 2
        kTwist = 3
        kThrottle = 4

    # Note: This is private upstream.
    # This copy is here because of the extra kNumAxes.
    class Axis(enum.IntEnum):
        """Represents an analog axis on a joystick"""

        kX = 0
        kY = 1
        kZ = 2
        kTwist = 3
        kThrottle = 4
        kNumAxes = 5

    class ButtonType(enum.IntEnum):
        """Represents a digital button on the Joystick"""

        kTrigger = 1
        kTop = 2

    # Note: This is private upstream.
    Button = ButtonType

    def __init__(self, port: int) -> None:
        """Construct an instance of a joystick.

        The joystick index is the USB port on the Driver Station.

        This constructor is intended for use by subclasses to configure the
        number of constants for axes and buttons.

        :param port: The port on the Driver Station that the joystick is
            plugged into.
        """
        super().__init__(port)

        self.axes = [0] * self.Axis.kNumAxes
        self.axes[self.Axis.kX] = self.kDefaultXChannel
        self.axes[self.Axis.kY] = self.kDefaultYChannel
        self.axes[self.Axis.kZ] = self.kDefaultZChannel
        self.axes[self.Axis.kTwist] = self.kDefaultTwistChannel
        self.axes[self.Axis.kThrottle] = self.kDefaultThrottleChannel

        hal.report(hal.UsageReporting.kResourceType_Joystick, port)

    def setXChannel(self, channel: int) -> None:
        """Set the channel associated with the X axis.

        :param channel: The channel to set the axis to.
        """
        self.axes[self.Axis.kX] = channel

    def setYChannel(self, channel: int) -> None:
        """Set the channel associated with the Y axis.

        :param channel: The channel to set the axis to.
        """
        self.axes[self.Axis.kY] = channel

    def setZChannel(self, channel: int) -> None:
        """Set the channel associated with the Z axis.

        :param channel: The channel to set the axis to.
        """
        self.axes[self.Axis.kZ] = channel

    def setThrottleChannel(self, channel: int) -> None:
        """Set the channel associated with the Throttle axis.

        :param channel: The channel to set the axis to.
        """
        self.axes[self.Axis.kThrottle] = channel

    def setTwistChannel(self, channel: int) -> None:
        """Set the channel associated with the Twist axis.

        :param channel: The channel to set the axis to.
        """
        self.axes[self.Axis.kTwist] = channel

    def setAxisChannel(self, axis, channel) -> None:
        """Set the channel associated with a specified axis.

        :param axis: The axis to set the channel for.
        :param channel: The channel to set the axis to.

        .. deprecated:: 2018.0.0
            Use the more specific axis channel setter functions
        """
        warnings.warn(
            "setAxisChannel is deprecated. Use the more specific axis channel setter functions",
            DeprecationWarning,
            stacklevel=2,
        )
        self.axes[axis] = channel

    def getXChannel(self) -> int:
        """Get the channel currently associated with the X axis

        :returns: The channel for the axis
        """
        return self.axes[self.Axis.kX]

    def getYChannel(self) -> int:
        """Get the channel currently associated with the Y axis

        :returns: The channel for the axis
        """
        return self.axes[self.Axis.kY]

    def getZChannel(self) -> int:
        """Get the channel currently associated with the Z axis

        :returns: The channel for the axis
        """
        return self.axes[self.Axis.kZ]

    def getThrottleChannel(self) -> int:
        """Get the channel currently associated with the Throttle axis

        :returns: The channel for the axis
        """
        return self.axes[self.Axis.kThrottle]

    def getTwistChannel(self) -> int:
        """Get the channel currently associated with the Twist axis

        :returns: The channel for the axis
        """
        return self.axes[self.Axis.kTwist]

    def getAxisChannel(self, axis: int) -> int:
        """Get the channel currently associated with the specified axis.

        :param axis: The axis to look up the channel for.
        :returns: The channel for the axis.
        
        ..deprecated:: 2018.0.0
            Use the more specific axis channel getter functions
        """
        warnings.warn(
            "getAxisChannel is deprecated. Use the more specific axis channel getter functions",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.axes[axis]

    def getX(self, hand=None) -> float:
        """Get the X value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The X value of the joystick.
        """
        return self.getRawAxis(self.axes[self.Axis.kX])

    def getY(self, hand=None) -> float:
        """Get the Y value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Y value of the joystick.
        """
        return self.getRawAxis(self.axes[self.Axis.kY])

    def getZ(self, hand=None) -> float:
        """Get the Z position of the HID

        :param hand: Unused
        :returns: the Z position
        """
        return self.getRawAxis(self.axes[self.Axis.kZ])

    def getTwist(self) -> float:
        """Get the twist value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Twist value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kTwist])

    def getThrottle(self) -> float:
        """Get the throttle value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Throttle value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kThrottle])

    def getAxis(self, axis) -> float:
        """For the current joystick, return the axis determined by the
        argument.

        This is for cases where the joystick axis is returned programmatically,
        otherwise one of the previous functions would be preferable (for
        example :func:`getX`).

        :param axis: The axis to read.
        :returns: The value of the axis.

        ..deprecated: 2018.0.0
            Use the more specific axis getter functions.
        """
        warnings.warn(
            "getAxis is deprecated. Use the more specific axis setter functions",
            DeprecationWarning,
            stacklevel=2,
        )

        if axis == self.AxisType.kX:
            return self.getX()
        elif axis == self.AxisType.kY:
            return self.getY()
        elif axis == self.AxisType.kZ:
            return self.getZ()
        elif axis == self.AxisType.kTwist:
            return self.getTwist()
        elif axis == self.AxisType.kThrottle:
            return self.getThrottle()
        else:
            raise ValueError(
                "Invalid axis specified! Must be one of wpilib.Joystick.AxisType, or use getRawAxis instead"
            )

    def getTrigger(self) -> bool:
        """Read the state of the trigger on the joystick.

        Look up which button has been assigned to the trigger and read its
        state.

        :returns: The state of the trigger.
        """
        return self.getRawButton(self.Button.kTrigger)

    def getTriggerPressed(self) -> bool:
        """Whether the trigger was pressed since the last check

        :returns: Whether the button was pressed since the last check
        """
        return self.getRawButtonPressed(self.Button.kTrigger)

    def getTriggerReleased(self) -> bool:
        """Whether the trigger was released since the last check.

        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kTrigger)

    def getTop(self) -> bool:
        """Read the state of the top button on the joystick.

        Look up which button has been assigned to the top and read its state.

        :returns: The state of the top button.
        """
        return self.getRawButton(self.Button.kTop)

    def getTopPressed(self) -> bool:
        """Whether the trigger was pressed since the last check

        :returns: Whether the button was pressed since the last check
        """
        return self.getRawButtonPressed(self.Button.kTop)

    def getTopReleased(self) -> bool:
        """Whether the trigger was released since the last check.

        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kTop)

    def getButton(self, button: ButtonType) -> bool:
        """Get buttons based on an enumerated type.

        The button type will be looked up in the list of buttons and then read.

        :param button: The type of button to read.
        :returns: The state of the button.

        ..deprecated: 2018.0.0
            Use Button enum values instead of ButtonType
        """
        warnings.warn(
            "getButton is deprecated. Use Button enum values instead of ButtonType",
            DeprecationWarning,
            stacklevel=2,
        )
        if button == self.ButtonType.kTrigger:
            return self.getTrigger()
        elif button == self.ButtonType.kTop:
            return self.getTop()
        else:
            raise ValueError(
                "Invalid button specified! Must be one of wpilib.Joystick.ButtonType, or use getRawButton instead"
            )

    def getMagnitude(self) -> float:
        """Get the magnitude of the direction vector formed by the joystick's
        current position relative to its origin.

        :returns: The magnitude of the direction vector
        """
        return math.hypot(self.getX(), self.getY())

    def getDirectionRadians(self) -> float:
        """Get the direction of the vector formed by the joystick and its
        origin in radians.

        :returns: The direction of the vector in radians
        """
        return math.atan2(self.getX(), -self.getY())

    def getDirectionDegrees(self) -> float:
        """Get the direction of the vector formed by the joystick and its
        origin in degrees.

        :returns: The direction of the vector in degrees
        """
        return math.degrees(self.getDirectionRadians())
