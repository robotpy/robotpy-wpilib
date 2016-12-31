# validated: 2016-12-31 JW 8f67f2c24cb9 athena/java/edu/wpi/first/wpilibj/AnalogOutput.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase

__all__ = ["AnalogOutput"]

def _freeAnalogOutput(port):
    hal.freeAnalogOutputPort(port)

class AnalogOutput(SensorBase):
    """Analog output"""

    channels = Resource(SensorBase.kAnalogOutputChannels)

    def __init__(self, channel):
        """Construct an analog output on a specified MXP channel.

        :param channel: The channel number to represent.
        """
        SensorBase.checkAnalogOutputChannel(channel)
        
        self.channel = channel

        port = hal.getPort(channel)
        self._port = hal.initializeAnalogOutputPort(port)

        LiveWindow.addSensorChannel("AnalogOutput", channel, self)
        hal.report(hal.UsageReporting.kResourceType_AnalogChannel,
                      channel, 1)
        
        self.__finalizer = weakref.finalize(self, _freeAnalogOutput, self._port)

    @property
    def port(self):
        if not self.__finalizer.alive:
            return None
        return self._port
    
    def free(self):
        """Channel destructor.
        """
        LiveWindow.removeComponent(self)
        if self.channel is None:
            return
        AnalogOutput.channels.free(self.channel)
        self.__finalizer()
        self.channel = None

    def getChannel(self):
        """Get the channel of this AnalogOutput.
        """
        return self.channel

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
