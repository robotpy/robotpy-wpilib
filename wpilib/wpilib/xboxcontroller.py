# validated: 2017-01-12 DS 8f67f2c24cb9 athena/java/edu/wpi/first/wpilibj/XboxController.java
import hal
from .driverstation import DriverStation
from .interfaces.gamepadbase import GamepadBase
from wpilib.interfaces.generichid import GenericHID


class XboxController(GamepadBase):
    """
        Handle input from Xbox 360 or Xbox One controllers connected to the Driver Station.

        This class handles Xbox input that comes from the Driver Station. Each time a value is
        requested the most recent value is returned. There is a single class instance for each controller
        and the mapping of ports to hardware buttons depends on the code in the Driver Station.
     """

    def __init__(self, port):
        """Construct an instance of an XBoxController. The XBoxController index is the USB port on the Driver Station.

        :param port: The port on the Driver Station that the joystick is plugged into
        """

        super().__init__(port)
        self.ds = DriverStation.getInstance()

        self.outputs = 0
        self.leftRumble = 0
        self.rightRumble = 0

        hal.report(hal.UsageReporting.kResourceType_Joystick, port)

    def getX(self, hand):
        """Get the X axis value of the controller.

        :param hand: Side of controller whose value should be returned
        :return: The X axis value of the controller
        :rtype: float
        """
        if hand == GenericHID.Hand.kLeft:
            return self.getRawAxis(0)
        else:
            return self.getRawAxis(4)

    def getY(self, hand):
        """Get the Y axis value of the controller.

        :param hand: Side of controller whose value should be returned
        :return: The Y axis value of the controller
        :rtype: float
        """
        if hand == GenericHID.Hand.kLeft:
            return self.getRawAxis(1)
        else:
            return self.getRawAxis(5)

    def getRawAxis(self, axis):
        """Get the value of the axis

        :param axis: The axis to read, starting at 0
        :return: The value of the axis
        :rtype: float
        """
        return self.ds.getStickAxis(self.port, axis)

    def getBumper(self, hand):
        """Read the values of the bumper button on the controller.

        :param hand: Side of controller whose value should be returned.
        :return: The state of the button
        :rtype: boolean
        """
        if hand == GenericHID.Hand.kLeft:
            return self.getRawButton(5)
        else:
            return self.getRawButton(6)

    def getRawButton(self, button):
        """Get the buttom value (starting at button 1)

        :param button: The button number to be read (starting at 1)
        :return: The state of the button
        :rtype: boolean
        """
        return self.ds.getStickButton(self.port, button)

    def getTriggerAxis(self, hand):
        """Get the trigger axis value of the controller.

        :param hand: Side of controller whose value should be returned
        :return: The trigger axis value of the controller
        :rtype: float
        """
        if hand == GenericHID.Hand.kLeft:
            return self.getRawAxis(2)
        else:
            return self.getRawAxis(3)

    def getAButton(self):
        """Read the value of the A button on the controller

        :return: The state of the A button
        :rtype: boolean
        """
        return self.getRawButton(1)

    def getBButton(self):
        """Read the value of the B button on the controller

        :return: The state of the B button
        :rtype: boolean
        """
        return self.getRawButton(2)

    def getXButton(self):
        """Read the value of the X button on the controller

        :return: The state of the X button
        :rtype: boolean
        """
        return self.getRawButton(3)

    def getYButton(self):
        """Read the value of the Y button on the controller

        :return: The state of the Y button
        :rtype: boolean
        """
        return self.getRawButton(4)

    def getStickButton(self, hand):
        """Read the values of the stick button on the controller

        :param hand: Side of the controller whose value should be returned
        :return: The state of the button
        :rtype: boolean
        """
        if hand == GenericHID.Hand.kLeft:
            return self.getRawButton(9)
        else:
            return self.getRawButton(10)

    def getBackButton(self):
        """Read the value of the back button on the controller

        :return: The state of the back button
        :rtype: boolean
        """
        return self.getRawButton(7)

    def getStartButton(self):
        """Read the value of the start button on the controller

        :return: The state of the start button
        :rtype: boolean
        """
        return self.getRawButton(8)

    def getPOV(self, pov):
        return self.ds.getStickPOV(self.port, pov)

    def getPOVCount(self):
        return self.ds.getPOVCount(self.port)

    def getType(self):
        return self.ds.getJoystickType(self.port)

    def getName(self):
        return self.ds.getJoystickName(self.port)

    def setOutput(self, outputNumber, value):
        self.outputs = ((self.outputs & ~(1 << (outputNumber - 1)))
                        | ((1 if value else 0) << (outputNumber - 1)))
        hal.setJoystickOutputs(self.port, self.outputs, self.leftRumble, self.rightRumble)

    def setOutputs(self, value):
        self.outputs = value
        hal.setJoystickOutputs(self.port, self.outputs, self.leftRumble, self.rightRumble)

    def setRumble(self, type_, value):
        if value < 0:
            value = 0
        if value > 1:
            value = 1

        if type_ == GenericHID.RumbleType.kLeftRumble:
            self.leftRumble = int(value * 65535)
        else:
            self.rightRumble = int(value * 65535)

        hal.setJoystickOutputs(
            self.port,
            self.outputs,
            self.leftRumble,
            self.rightRumble)
