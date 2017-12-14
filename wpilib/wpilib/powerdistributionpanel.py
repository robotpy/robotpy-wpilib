# validated: 2017-12-12 EN f9bece2ffbf7 edu/wpi/first/wpilibj/PowerDistributionPanel.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from functools import partial
from .sensorbase import SensorBase

__all__ = ["PowerDistributionPanel"]

class PowerDistributionPanel(SensorBase):
    """
        Use to obtain voltage, current, temperature, power, and energy from the
        Power Distribution Panel over CAN
    """

    def __init__(self, module=0):
        """
            :param module: CAN ID of the PDP
            :type module: int
        """
        super().__init__()
        self.module = module
        SensorBase.checkPDPModule(module)
        hal.initializePDP(module)
        self.setName("PowerDistributionPanel", module)

    def getVoltage(self):
        """
            Query the input voltage of the PDP

            :returns: The voltage of the PDP in volts
            :rtype: float
        """
        return hal.getPDPVoltage(self.module)

    def getTemperature(self):
        """
            Query the temperature of the PDP

            :returns: The temperature of the PDP in degrees Celsius
            :rtype: float
        """
        return hal.getPDPTemperature(self.module)

    def getCurrent(self, channel):
        """
            Query the current of a single channel of the PDP

            :returns: The current of one of the PDP channels (channels 0-15)
                      in Amperes
            :rtype: float
        """
        SensorBase.checkPDPChannel(channel)
        return hal.getPDPChannelCurrent(self.module, channel)
    
    def getTotalCurrent(self):
        """
            Query the current of all monitored PDP channels (0-15)

            :returns: The total current drawn from the PDP channels in Amperes
            :rtype: float
        """
        return hal.getPDPTotalCurrent(self.module)
    
    def getTotalPower(self):
        """
            Query the total power drawn from the monitored PDP channels

            :returns: The total power drawn from the PDP channels in Watts
            :rtype: float
        """
        return hal.getPDPTotalPower(self.module)
    
    def getTotalEnergy(self):
        """
            Query the total energy drawn from the monitored PDP channels

            :returns: The total energy drawn from the PDP channels in Joules
            :rtype: float
        """
        return hal.getPDPTotalEnergy(self.module)
    
    def resetTotalEnergy(self):
        """
            Reset the total energy to 0
        """
        hal.resetPDPTotalEnergy(self.module)
    
    def clearStickyFaults(self):
        """
            Clear all pdp sticky faults
        """
        hal.clearPDPStickyFaults(self.module)

    def initSendable(self, builder):
        builder.setSmartDashboardType("PowerDistributionPanel")
        for chan in range(self.kPDPChannels):
            builder.addDoubleProperty("Chan%s" % (chan,), partial(self.getCurrent, chan), None)
        builder.addDoubleProperty("Voltage", self.getVoltage, None)
        builder.addDoubleProperty("TotalCurrent", self.getTotalCurrent, None)
