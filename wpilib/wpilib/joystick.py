# validated: 2017-11-13 TW 595b1df380f7 edu/wpi/first/wpilibj/Joystick.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

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

    kDefaultXAxis = 0
    kDefaultYAxis = 1
    kDefaultZAxis = 2
    kDefaultTwistAxis = 2
    kDefaultThrottleAxis = 3
    kDefaultTriggerButton = 1
    kDefaultTopButton = 2

    class AxisType:
        """Represents an analog axis on a joystick."""
        kX = 0
        kY = 1
        kZ = 2
        kTwist = 3
        kThrottle = 4

    class Axis:
        """Represents an analog axis on a joystick"""
        kX = 0
        kY = 1
        kZ = 2
        kTwist = 3
        kThrottle = 4
        kNumAxis = 5

    class ButtonType:
        """Represents a digital button on the Joystick"""
        kTrigger = 1
        kTop = 2

    class Button:
        """Represents a digital button on the Joystick"""
        kTrigger = 1
        kTop = 2

    def __init__(self, port):
        """Construct an instance of a joystick.

        The joystick index is the USB port on the Driver Station.

        This constructor is intended for use by subclasses to configure the
        number of constants for axes and buttons.

        :param port: The port on the Driver Station that the joystick is
            plugged into.
        :type  port: int
        :param numAxisTypes: The number of axis types.
        :type  numAxisTypes: int
        :param numButtonTypes: The number of button types.
        :type  numButtonTypes: int
        """
        super().__init__(port)
        from .driverstation import DriverStation
        self.ds = DriverStation.getInstance()

        self.axes = [0] * self.Axis.kNumAxis
        self.axes[self.Axis.kX] = self.kDefaultXAxis
        self.axes[self.Axis.kY] = self.kDefaultYAxis
        self.axes[self.Axis.kZ] = self.kDefaultZAxis
        self.axes[self.Axis.kTwist] = self.kDefaultTwistAxis
        self.axes[self.Axis.kThrottle] = self.kDefaultThrottleAxis

        self.outputs = 0
        self.leftRumble = 0
        self.rightRumble = 0

        hal.report(hal.UsageReporting.kResourceType_Joystick, port)

    def setXChannel(self, channel):
        """Set the channel associated with the X axis.

        :param channel: The channel to set the axis to.
        :type channel: int
        """
        self.axes[self.Axis.kX] = channel

    def setYChannel(self, channel):
        """Set the channel associated with the Y axis.

        :param channel: The channel to set the axis to.
        :type channel: int
        """
        self.axes[self.Axis.kY] = channel

    def setZChannel(self, channel):
        """Set the channel associated with the Z axis.

        :param channel: The channel to set the axis to.
        :type channel: int
        """
        self.axes[self.Axis.kZ] = channel

    def setThrottleChannel(self, channel):
        """Set the channel associated with the Throttle axis.

        :param channel: The channel to set the axis to.
        :type channel: int
        """
        self.axes[self.Axis.kThrottle] = channel

    def setTwistChannel(self, channel):
        """Set the channel associated with the Twist axis.

        :param channel: The channel to set the axis to.
        :type channel: int
        :rtype: int
        """
        self.axes[self.Axis.kTwist] = channel

    def setAxisChannel(self, axis, channel):
        """Set the channel associated with a specified axis.

        :param axis: The axis to set the channel for.
        :type  axis: int
        :param channel: The channel to set the axis to.
        :type  channel: int

        .. deprecated:: 2018.0.0
            Use the more specific axis channel setter functions
        """
        warnings.warn("setAxisChannel is deprecated. Use the more specific axis channel setter functions",
                      DeprecationWarning, stacklevel=2)
        self.axes[axis] = channel

    def getXChannel(self):
        """Get the channel currently associated with the X axis

        :returns: The channel for the axis
        :rtype: int
        """
        return self.axes[self.Axis.kX]

    def getYChannel(self):
        """Get the channel currently associated with the Y axis

        :returns: The channel for the axis
        :rtype: int
        """
        return self.axes[self.Axis.kY]

    def getZChannel(self):
        """Get the channel currently associated with the Z axis

        :returns: The channel for the axis
        :rtype: int
        """
        return self.axes[self.Axis.kZ]

    def getThrottleChannel(self):
        """Get the channel currently associated with the Throttle axis

        :returns: The channel for the axis
        :rtype: int
        """
        return self.axes[self.Axis.kThrottle]

    def getTwistChannel(self):
        """Get the channel currently associated with the Twist axis

        :returns: The channel for the axis
        :rtype: int
        """
        return self.axes[self.Axis.kTwist]

    def getAxisChannel(self, axis):
        """Get the channel currently associated with the specified axis.

        :param axis: The axis to look up the channel for.
        :type  axis: int
        :returns: The channel for the axis.
        :rtype: int
        
        ..deprecated:: 2018.0.0
            Use the more specific axis channel getter functions
        """
        warnings.warn("getAxisChannel is deprecated. Use the more specific axis channel getter functions",
                      DeprecationWarning, stacklevel=2)
        return self.axes[axis]

    def getX(self, hand=None):
        """Get the X value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The X value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.Axis.kX])

    def getY(self, hand=None):
        """Get the Y value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Y value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.Axis.kY])

    def getZ(self, hand=None):
        """Get the Z position of the HID

        :param hand: Unused
        :returns: the Z position
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.Axis.kZ])

    def getTwist(self):
        """Get the twist value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Twist value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.AxisType.kTwist])

    def getThrottle(self):
        """Get the throttle value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Throttle value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.AxisType.kThrottle])

    def getAxis(self, axis):
        """For the current joystick, return the axis determined by the
        argument.

        This is for cases where the joystick axis is returned programmatically,
        otherwise one of the previous functions would be preferable (for
        example :func:`getX`).

        :param axis: The axis to read.
        :type axis: :class:`Joystick.AxisType`
        :returns: The value of the axis.
        :rtype: float

        ..deprecated: 2018.0.0
            Use the more specific axis getter functions.
        """
        warnings.warn("getAxis is deprecated. Use the more specific axis setter functions",
                      DeprecationWarning, stacklevel=2)

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
                "Invalid axis specified! Must be one of wpilib.Joystick.AxisType, or use getRawAxis instead")

    def getTrigger(self):
        """Read the state of the trigger on the joystick.

        Look up which button has been assigned to the trigger and read its
        state.

        :returns: The state of the trigger.
        :rtype: bool
        """
        return self.getRawButton(self.Button.kTrigger)

    def getTriggerPressed(self):
        """Whether the trigger was pressed since the last check

        :returns: Whether the button was pressed since the last check
        """
        return self.getRawButtonPressed(self.Button.kTrigger)

    def getTriggerReleased(self):
        """Whether the trigger was released since the last check.

        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kTrigger)

    def getTop(self):
        """Read the state of the top button on the joystick.

        Look up which button has been assigned to the top and read its state.

        :returns: The state of the top button.
        :rtype: bool
        """
        return self.getRawButton(self.Button.kTop)

    def getTopPressed(self):
        """Whether the trigger was pressed since the last check

        :returns: Whether the button was pressed since the last check
        """
        return self.getRawButtonPressed(self.Button.kTop)

    def getTopReleased(self):
        """Whether the trigger was released since the last check.

        :returns: Whether the button was released since the last check.
        """
        return self.getRawButtonReleased(self.Button.kTop)

    def getButton(self, button):
        """Get buttons based on an enumerated type.

        The button type will be looked up in the list of buttons and then read.

        :param button: The type of button to read.
        :type  button: :class:`.Joystick.ButtonType`
        :returns: The state of the button.
        :rtype: bool

        ..deprecated: 2018.0.0
            Use Button enum values instead of ButtonType
        """
        warnings.warn("getButton is deprecated. Use Button enum values instead of ButtonType",
                      DeprecationWarning, stacklevel=2)
        if button == self.ButtonType.kTrigger:
            return self.getTrigger()
        elif button == self.ButtonType.kTop:
            return self.getTop()
        else:
            raise ValueError(
                "Invalid button specified! Must be one of wpilib.Joystick.ButtonType, or use getRawButton instead")

    def getMagnitude(self):
        """Get the magnitude of the direction vector formed by the joystick's
        current position relative to its origin.

        :returns: The magnitude of the direction vector
        :rtype: float
        """
        return math.hypot(self.getX(), self.getY())

    def getDirectionRadians(self):
        """Get the direction of the vector formed by the joystick and its
        origin in radians.

        :returns: The direction of the vector in radians
        :rtype: float
        """
        return math.atan2(self.getX(), -self.getY())

    def getDirectionDegrees(self):
        """Get the direction of the vector formed by the joystick and its
        origin in degrees.

        :returns: The direction of the vector in degrees
        :rtype: float
        """
        return math.degrees(self.getDirectionRadians())
