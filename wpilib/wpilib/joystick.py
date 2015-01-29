#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import math

__all__ = ["Joystick"]

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

    class RumbleType:
        """Represents a rumble output on the Joystick"""
        kLeftRumble_val = 0
        kRightRumble_val = 1



    def __init__(self, port, numAxisTypes=None, numButtonTypes=None):
        """Construct an instance of a joystick.

        The joystick index is the usb port on the drivers station.

        This constructor is intended for use by subclasses to configure the
        number of constants for axes and buttons.

        :param port: The port on the driver station that the joystick is
            plugged into.
        :type  port: int
        :param numAxisTypes: The number of axis types.
        :type  numAxisTypes: int
        :param numButtonTypes: The number of button types.
        :type  numButtonTypes: int
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

        self.outputs = 0
        self.leftRumble = 0
        self.rightRumble = 0

        hal.HALReport(hal.HALUsageReporting.kResourceType_Joystick, port)

    def getX(self, hand=None):
        """Get the X value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The X value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.AxisType.kX])

    def getY(self, hand=None):
        """Get the Y value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Y value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.AxisType.kY])

    def getZ(self, hand=None):
        """Get the Z value of the joystick.

        This depends on the mapping of the joystick connected to the current
        port.

        :param hand: Unused
        :returns: The Z value of the joystick.
        :rtype: float
        """
        return self.getRawAxis(self.axes[self.AxisType.kZ])

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

    def getRawAxis(self, axis):
        """Get the value of the axis.

        :param axis: The axis to read, starting at 0.
        :type  axis: int
        :returns: The value of the axis.
        :rtype: float
        """
        return self.ds.getStickAxis(self.port, axis)

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
            raise ValueError("Invalid axis specified! Must be one of wpilib.Joystick.AxisType, or use getRawAxis instead")
        
    def getAxisCount(self):
        """For the current joystick, return the number of axis"""
        return self.ds.getStickAxisCount(self.port)

    def getTrigger(self, hand=None):
        """Read the state of the trigger on the joystick.

        Look up which button has been assigned to the trigger and read its
        state.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the trigger.
        :rtype: bool
        """
        return self.getRawButton(self.buttons[self.ButtonType.kTrigger])

    def getTop(self, hand=None):
        """Read the state of the top button on the joystick.

        Look up which button has been assigned to the top and read its state.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the top button.
        :rtype: bool
        """
        return self.getRawButton(self.buttons[self.ButtonType.kTop])

    def getBumper(self, hand=None):
        """This is not supported for the Joystick.

        This method is only here to complete the GenericHID interface.

        :param hand: This parameter is ignored for the Joystick class and is
            only here to complete the GenericHID interface.
        :returns: The state of the bumper (always False)
        :rtype: bool
        """
        return False

    def getRawButton(self, button):
        """Get the button value (starting at button 1).

        The buttons are returned in a single 16 bit value with one bit
        representing the state of each button. The appropriate button is
        returned as a boolean value.

        :param button: The button number to be read (starting at 1).
        :type  button: int
        :returns: The state of the button.
        :rtype: bool
        """
        return self.ds.getStickButton(self.port, button)
    
    def getButtonCount(self):
        """For the current joystick, return the number of buttons
        
        :rtype int
        """
        return self.ds.getStickButtonCount(self.port)

    def getPOV(self, pov=0):
        """Get the state of a POV on the joystick.

        :param pov: which POV (default is 0)
        :type  pov: int
        :returns: The angle of the POV in degrees, or -1 if the POV is not
                  pressed.
        :rtype: float
        """
        return self.ds.getStickPOV(self.port, pov)
    
    def getPOVCount(self):
        """For the current joystick, return the number of POVs
        
        :rtype: int
        """
        return self.ds.getStickPOVCount(self.port)

    def getButton(self, button):
        """Get buttons based on an enumerated type.

        The button type will be looked up in the list of buttons and then read.

        :param button: The type of button to read.
        :type  button: :class:`.Joystick.ButtonType`
        :returns: The state of the button.
        :rtype: bool
        """
        if button == self.ButtonType.kTrigger:
            return self.getTrigger()
        elif button == self.ButtonType.kTop:
            return self.getTop()
        else:
            raise ValueError("Invalid button specified! Must be one of wpilib.Joystick.ButtonType, or use getRawButton instead")

    def getMagnitude(self):
        """Get the magnitude of the direction vector formed by the joystick's
        current position relative to its origin.

        :returns: The magnitude of the direction vector
        :rtype: float
        """
        return math.sqrt(math.pow(self.getX(), 2) + math.pow(self.getY(), 2))

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

    def getAxisChannel(self, axis):
        """Get the channel currently associated with the specified axis.

        :param axis: The axis to look up the channel for.
        :type  axis: int
        :returns: The channel for the axis.
        :rtype: int
        """
        return self.axes[axis]

    def setAxisChannel(self, axis, channel):
        """Set the channel associated with a specified axis.

        :param axis: The axis to set the channel for.
        :type  axis: int
        :param channel: The channel to set the axis to.
        :type  channel: int
        """
        self.axes[axis] = channel

    def setRumble(self, type, value):
        """Set the rumble output for the joystick. The DS currently supports 2 rumble values,
        left rumble and right rumble
        
        :param type: Which rumble value to set
        :type  type: :class:`.Joystick.RumbleType`
        :param value: The normalized value (0 to 1) to set the rumble to
        :type  value: float
        """
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        if type == self.RumbleType.kLeftRumble_val:
            self.leftRumble = int(value*65535)
        elif type == self.RumbleType.kRightRumble_val:
            self.rightRumble = int(value*65535)
        else:
            raise ValueError("Invalid wpilib.Joystick.RumbleType: {}".format(type))
        self.flush_outputs()

    def setOutput(self, outputNumber, value):
        """Set a single HID output value for the joystick.
        
        :param outputNumber: The index of the output to set (1-32)
        :param value: The value to set the output to.
        """
        self.outputs = (self.outputs & ~(value << (outputNumber-1))) | (value << (outputNumber-1))
        self.flush_outputs()

    def setOutputs(self, value):
        """Set all HID output values for the joystick.
        
        :param value: The 32 bit output value (1 bit for each output)
        :type  value: int
        """
        self.outputs = value
        self.flush_outputs()

    def flush_outputs(self):
        """Flush all joystick HID & rumble output values to the HAL"""
        hal.HALSetJoystickOutputs(self.port, self.outputs, self.leftRumble, self.rightRumble)
