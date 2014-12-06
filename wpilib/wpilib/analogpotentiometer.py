#----------------------------------------------------------------------------*/
# Copyright (c) FIRST 2008-2014. All Rights Reserved.                        */
# Open Source Software - may be modified and shared by FRC teams. The code   */
# must be accompanied by the FIRST BSD license file in the root directory of */
# the project.                                                               */
#----------------------------------------------------------------------------*/

from .analoginput import AnalogInput
from .livewindowsendable import LiveWindowSendable

__all__ = ["AnalogPotentiometer"]

class AnalogPotentiometer(LiveWindowSendable):
    """Class for reading analog potentiometers. Analog potentiometers read
    in an analog voltage that corresponds to a position. Usually the
    position is either degrees or meters. However, if no conversion is
    given it remains volts.
    
    .. not_implemented: initPot
    """

    def __init__(self, channel, scale=1.0, offset=0.0):
        """AnalogPotentiometer constructor.

        Use the scaling and offset values so that the output produces
        meaningful values. I.E: you have a 270 degree potentiometer and
        you want the output to be degrees with the halfway point as 0
        degrees. The scale value is 270.0(degrees)/5.0(volts) and the
        offset is -135.0 since the halfway point after scaling is 135
        degrees.

        :param channel: The analog channel this potentiometer is plugged into.
            May be either a channel index or an AnalogInput instance.
        :param scale: The scaling to multiply the voltage by to get a
            meaningful unit.  Defaults to 1.0 if unspecified.
        :param offset: The offset to add to the scaled value for controlling
            the zero value.  Defaults to 0.0 if unspecified.
        """
        if not hasattr(channel, "getVoltage"):
            channel = AnalogInput(channel)
        self.analog_input = channel
        self.scale = scale
        self.offset = offset

    def get(self):
        """Get the current reading of the potentiomere.

        :returns: The current position of the potentiometer.
        """
        return self.analog_input.getVoltage() * self.scale + self.offset

    def pidGet(self):
        """Implement the PIDSource interface.

        :returns: The current reading.
        """
        return self.get()

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Analog Input"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.get())

    def startLiveWindowMode(self):
        # don't have to do anything special when entering the LiveWindow
        pass

    def stopLiveWindowMode(self):
        # don't have to do anything special when exiting the LiveWindow
        pass
