# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/AnalogOutput.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2014-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import weakref

from .resource import Resource
from .sendablebase import SendableBase
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder

__all__ = ["AnalogOutput"]


def _freeAnalogOutput(port: hal.AnalogOutputHandle) -> None:
    hal.freeAnalogOutputPort(port)


class AnalogOutput(SendableBase):
    """Analog output"""

    channels = Resource(SensorUtil.kAnalogOutputChannels)

    def __init__(self, channel: int) -> None:
        """Construct an analog output on a specified MXP channel.

        :param channel: The channel number to represent.
        """
        super().__init__()
        SensorUtil.checkAnalogOutputChannel(channel)

        self.channel = channel

        port = hal.getPort(channel)
        self.port = hal.initializeAnalogOutputPort(port)

        self.setName("AnalogOutput", channel)
        hal.report(hal.UsageReporting.kResourceType_AnalogChannel, channel, 1)

        self.__finalizer = weakref.finalize(self, _freeAnalogOutput, self.port)

    def close(self) -> None:
        """Channel destructor.
        """
        super().close()
        if self.channel is None:
            return
        AnalogOutput.channels.free(self.channel)
        self.__finalizer()
        self.channel = None
        self.port = None

    def getChannel(self) -> int:
        """Get the channel of this AnalogOutput.
        """
        return self.channel

    def setVoltage(self, voltage: float) -> None:
        hal.setAnalogOutput(self.port, voltage)

    def getVoltage(self) -> float:
        return hal.getAnalogOutput(self.port)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Analog Output")
        builder.addDoubleProperty("Value", self.getVoltage, self.setVoltage)
