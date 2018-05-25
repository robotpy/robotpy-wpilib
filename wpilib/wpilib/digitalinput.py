# validated: 2018-09-18 EN ecfe95383cdf edu/wpi/first/wpilibj/DigitalInput.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .digitalsource import DigitalSource
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder

__all__ = ["DigitalInput"]


class DigitalInput(DigitalSource):
    """Reads a digital input.
    
    This class will read digital inputs and return the current value on the
    channel. Other devices such as encoders, gear tooth sensors, etc. that
    are implemented elsewhere will automatically allocate digital inputs
    and outputs as required. This class is only for devices like switches
    etc. that aren't implemented anywhere else.
    """

    def __init__(self, channel: int) -> None:
        """Create an instance of a Digital Input class. Creates a digital
        input given a channel.

        :param channel: the DIO channel for the digital input. 0-9 are on-board, 10-25 are on the MXP
        """

        super().__init__()
        SensorUtil.checkDigitalChannel(channel)
        self.channel = channel

        self.handle = hal.initializeDIOPort(hal.getPort(channel), True)

        hal.report(hal.UsageReporting.kResourceType_DigitalInput, channel)
        self.setName("DigitalInput", channel)

    def close(self) -> None:
        super().close()

        if self.interrupt:
            self.cancelInterrupts()

        hal.freeDIOPort(self.handle)
        self.handle = 0

    def get(self) -> bool:
        """Get the value from a digital input channel. Retrieve the value of
        a single digital input channel from the FPGA.

        :returns: the state of the digital input
        """
        return hal.getDIO(self.handle)

    def getChannel(self) -> int:
        """Get the channel of the digital input.

        :returns: The GPIO channel number that this object represents.
        """
        return self.channel

    def getAnalogTriggerTypeForRouting(self) -> int:
        """Get the analog trigger type.

        :returns: false
        """
        return 0

    def isAnalogTrigger(self) -> bool:
        """Is this an analog trigger.

        :returns: true if this is an analog trigger
        """
        return False

    def getPortHandleForRouting(self) -> hal.DigitalHandle:
        """Get the HAL Port Handle.

        :return: The HAL Handle to the specified source
        """
        return self.handle

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Digital Input")
        builder.addBooleanProperty("Value", self.get, None)
