# validated: 2018-09-09 EN 3eae079db478 edu/wpi/first/wpilibj/PowerDistributionPanel.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from functools import partial
from .sendablebase import SendableBase
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder

__all__ = ["PowerDistributionPanel"]


class PowerDistributionPanel(SendableBase):
    """
        Use to obtain voltage, current, temperature, power, and energy from the
        Power Distribution Panel over CAN
    """

    def __init__(self, module: int = 0) -> None:
        """
            :param module: CAN ID of the PDP
        """
        super().__init__()
        SensorUtil.checkPDPModule(module)
        self.handle = hal.initializePDP(module)
        hal.report(hal.UsageReporting.kResourceType_PDP, module)
        self.setName("PowerDistributionPanel", module)

    def getVoltage(self) -> float:
        """
            Query the input voltage of the PDP

            :returns: The voltage of the PDP in volts
        """
        return hal.getPDPVoltage(self.handle)

    def getTemperature(self) -> float:
        """
            Query the temperature of the PDP

            :returns: The temperature of the PDP in degrees Celsius
        """
        return hal.getPDPTemperature(self.handle)

    def getCurrent(self, channel: int) -> float:
        """
            Query the current of a single channel of the PDP

            :returns: The current of one of the PDP channels (channels 0-15)
                      in Amperes
        """
        SensorUtil.checkPDPChannel(channel)
        return hal.getPDPChannelCurrent(self.handle, channel)

    def getTotalCurrent(self) -> float:
        """
            Query the current of all monitored PDP channels (0-15)

            :returns: The total current drawn from the PDP channels in Amperes
        """
        return hal.getPDPTotalCurrent(self.handle)

    def getTotalPower(self) -> float:
        """
            Query the total power drawn from the monitored PDP channels

            :returns: The total power drawn from the PDP channels in Watts
        """
        return hal.getPDPTotalPower(self.handle)

    def getTotalEnergy(self) -> float:
        """
            Query the total energy drawn from the monitored PDP channels

            :returns: The total energy drawn from the PDP channels in Joules
        """
        return hal.getPDPTotalEnergy(self.handle)

    def resetTotalEnergy(self) -> None:
        """
            Reset the total energy to 0
        """
        hal.resetPDPTotalEnergy(self.handle)

    def clearStickyFaults(self) -> None:
        """
            Clear all pdp sticky faults
        """
        hal.clearPDPStickyFaults(self.handle)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("PowerDistributionPanel")
        for chan in range(SensorUtil.kPDPChannels):
            builder.addDoubleProperty(
                "Chan%s" % (chan,), partial(self.getCurrent, chan), None
            )
        builder.addDoubleProperty("Voltage", self.getVoltage, None)
        builder.addDoubleProperty("TotalCurrent", self.getTotalCurrent, None)
