#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import math

class Joystick:
    """Handle input from standard Joysticks connected to the Driver Station.
    This class handles standard input that comes from the Driver Station. Each
    time a value is requested the most recent value is returned. There is a
    single class instance for each joystick and the mapping of ports to
    hardware buttons depends on the code in the driver station.
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
        kNumAxis = 5

    class ButtonType:
        """Represents a digital button on the Joystick"""
        kTrigger = 0
        kTop = 1
        kNumButton = 2

    def __init__(self, port, numAxisTypes=None, numButtonTypes=None):
        """Construct an instance of a joystick.

        The joystick index is the usb port on the drivers station.

        This constructor is intended for use by subclasses to configure the
        number of constants for axes and buttons.

        :param port: The port on the driver station that the joystick is
            plugged into.
        :param numAxisTypes: The number of axis types.
        :param numButtonTypes: The number of button types.
        """
        from .driverstation import DriverStation
        self.ds = DriverStation.getInstance()
        self.port = port

        if numAxisTypes is None:
            self.axes = [0]*self.AxisType.kNumAxis
            self.axes[self.AxisType.kX] = self.kDefaultXAxis
            self.axes[self.AxisType.kY] = self.kDefaultYAxis
            self.axes[self.AxisType.kZ] = self.kDefaultZAxis
            self.axes[self.AxisType.kTwist] = self.kDefaultTwistAxis
            self.axes[self.AxisType.kThrottle] = self.kDefaultThrottleAxis
        else:
            self.axes = [0]*numAxisTypes

        if numButtonTypes is None:
            self.buttons = [0]*self.ButtonType.kNumButton
            self.buttons[self.ButtonType.kTrigger] = self.kDefaultTriggerButton
            self.buttons[self.ButtonType.kTop] = self.kDefaultTopButton
        else:
            self.buttons = [0]*numButtonTypes

        hal.HALReport(hal.HALUsageReporting.kResourceType_Joystick, port)

    def getX(self, hand=None):
        """Get the X value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The X value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kX])

    def getY(self, hand=None):
        """Get the Y value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Y value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kY])

    def getZ(self, hand=None):
        """Get the Z value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Z value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kZ])

    def getTwist(self):
        """Get the twist value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Twist value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kTwist])

    def getThrottle(self):
        """Get the throttle value of the current joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :returns: The Throttle value of the joystick.
        """
        return self.getRawAxis(self.axes[self.AxisType.kThrottle])

    def getRawAxis(self, axis):
        """Get the value of the axis.

        :param axis: The axis to read, starting at 0.
        :returns: The value of the axis.
        """
        return self.ds.getStickAxis(self.port, axis)

    def getAxis(self, axis):
        """For the current joystick, return the axis determined by the
        argument.

        This is for cases where the joystick axis is returned programatically,
        otherwise one of the previous functions would be preferable (for
        example :func:`getX`).

        :param axis: The axis to read.
        :returns: The value of the axis.
        """
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
            return 0.0

    def getTrigger(self, hand=None):
        """Read the state of the trigger on the joystick.

        Look up which button has been assigned to the trigger and read its
        state.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the trigger.
        """
        return self.getRawButton(self.buttons[self.ButtonType.kTrigger])

    def getTop(self, hand=None):
        """Read the state of the top button on the joystick.

        Look up which button has been assigned to the top and read its state.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the top button.
        """
        return self.getRawButton(self.buttons[self.ButtonType.kTop])

    def getBumper(self, hand=None):
        """This is not supported for the Joystick.

        This method is only here to complete the GenericHID interface.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the bumper (always False)
        """
        return False

    def getRawButton(self, button):
        """Get the button value for buttons 1 through 12.

        The buttons are returned in a single 16 bit value with one bit
        representing the state of each button. The appropriate button is
        returned as a boolean value.

        :param button: The button number to be read.
        :returns: The state of the button.
        """
        return ((0x1 << (button - 1)) & self.ds.getStickButtons(self.port)) != 0

    def getPOV(self, pov=0):
        """Get the state of a POV on the joystick.

        :param pov: which POV (default is 0)
        :returns: The angle of the POV in degrees, or -1 if the POV is not
        pressed.
        """
        return self.ds.getStickPOV(self.port, pov)

    def getButton(self, button):
        """Get buttons based on an enumerated type.

        The button type will be looked up in the list of buttons and then read.

        :param button: The type of button to read.
        :returns: The state of the button.
        """
        if button == self.ButtonType.kTrigger:
            return self.getTrigger()
        elif button == self.ButtonType.kTop:
            return self.getTop()
        else:
            return False

    def getMagnitude(self):
        """Get the magnitude of the direction vector formed by the joystick's
        current position relative to its origin.

        :returns: The magnitude of the direction vector
        """
        return math.sqrt(math.pow(self.getX(), 2) + math.pow(self.getY(), 2))

    def getDirectionRadians(self):
        """Get the direction of the vector formed by the joystick and its
        origin in radians.

        :returns: The direction of the vector in radians
        """
        return math.atan2(self.getX(), -self.getY())

    def getDirectionDegrees(self):
        """Get the direction of the vector formed by the joystick and its
        origin in degrees.

        :returns: The direction of the vector in degrees
        """
        return math.degrees(self.getDirectionRadians())

    def getAxisChannel(self, axis):
        """Get the channel currently associated with the specified axis.

        :param axis: The axis to look up the channel for.
        :returns: The channel fr the axis.
        """
        return self.axes[axis]

    def setAxisChannel(self, axis, channel):
        """Set the channel associated with a specified axis.

        :param axis: The axis to set the channel for.
        :param channel: The channel to set the axis to.
        """
        self.axes[axis] = channel
