# validated: 2017-12-27 TW f9bece2ffbf7 edu/wpi/first/wpilibj/AnalogOutput.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

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
        super().__init__()
        SensorBase.checkAnalogOutputChannel(channel)
        
        self.channel = channel

        port = hal.getPort(channel)
        self._port = hal.initializeAnalogOutputPort(port)

        self.setName("AnalogOutput", channel)
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
        super().free()
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

    def initSendable(self, builder):
        builder.setSmartDashboardType("Analog Output")
        builder.addDoubleProperty("Value", self.getVoltage, self.setVoltage)

