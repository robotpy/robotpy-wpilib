#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase

__all__ = ["AnalogOutput"]

class AnalogOutput(SensorBase):
    """Analog output"""

    channels = Resource(SensorBase.kAnalogOutputChannels)

    def __init__(self, channel):
        """Construct an analog output on a specified MXP channel.

        :param channel: The channel number to represent.
        """
        if not hal.checkAnalogOutputChannel(channel):
            raise IndexError("Analog output channel %d cannot be allocated. Channel is not present." % channel)
        try:
            AnalogOutput.channels.allocate(self, channel)
        except IndexError as e:
            raise IndexError("Analog output channel %d is already allocated" % channel) from e

        self.channel = channel

        port = hal.getPort(channel)
        self.port = hal.initializeAnalogOutputPort(port)

        LiveWindow.addSensorChannel("AnalogOutput", channel, self)
        hal.HALReport(hal.HALUsageReporting.kResourceType_AnalogChannel,
                      channel, 1)

    def free(self):
        """Channel destructor.
        """
        if self.channel is None:
            return
        AnalogOutput.channels.free(self.channel)
        self.channel = None

    def setVoltage(self, voltage):
        hal.setAnalogOutput(self.port, voltage)

    def getVoltage(self):
        return hal.getAnalogOutput(self.port)

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Analog Output"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.getVoltage())

    def startLiveWindowMode(self):
        # Analog Channels don't have to do anything special when entering the
        # LiveWindow.
        pass

    def stopLiveWindowMode(self):
        # Analog Channels don't have to do anything special when exiting the
        # LiveWindow.
        pass
