#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .digitalsource import DigitalSource
from .livewindow import LiveWindow

__all__ = ["DigitalInput"]

class DigitalInput(DigitalSource):
    """Reads a digital input.
    
    This class will read digital inputs and return the current value on the
    channel. Other devices such as encoders, gear tooth sensors, etc. that
    are implemented elsewhere will automatically allocate digital inputs
    and outputs as required. This class is only for devices like switches
    etc. that aren't implemented anywhere else.
    """

    def __init__(self, channel):
        """Create an instance of a Digital Input class. Creates a digital
        input given a channel.

        :param channel: the DIO channel for the digital input. 0-9 are on-board, 10-25 are on the MXP
        :type  channel: int
        """
        super().__init__(channel, True)

        hal.HALReport(hal.HALUsageReporting.kResourceType_DigitalInput,
                      channel)
        LiveWindow.addSensorChannel("DigitalInput", channel, self)

    def get(self):
        """Get the value from a digital input channel. Retrieve the value of
        a single digital input channel from the FPGA.

        :returns: the state of the digital input
        :rtype: bool
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return hal.getDIO(self.port)

    def getChannel(self):
        """Get the channel of the digital input

        :returns: The GPIO channel number that this object represents.
        :rtype: int
        """
        return self.channel

    def getAnalogTriggerForRouting(self):
        return False

    # Live Window code, only does anything if live window is activated.
    def getSmartDashboardType(self):
        return "Digital Input"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putBoolean("Value", self.get())
