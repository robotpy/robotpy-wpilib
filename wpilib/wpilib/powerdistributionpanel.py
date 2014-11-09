#----------------------------------------------------------------------------
# Copyright (c) FIRST 2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .sensorbase import SensorBase

__all__ = ["PowerDistributionPanel"]

class PowerDistributionPanel(SensorBase):
    """Class for getting voltage, current, and temperature from the CAN PDP"""

    def getVoltage(self):
        """:returns: The voltage of the PDP
        """
        return hal.getPDPVoltage()

    def getTemperature(self):
        """:returns: The temperature of the PDP in degrees Celsius
        """
        return hal.getPDPTemperature()

    def getCurrent(self, channel):
        """
            :returns: The current of one of the PDP channels (channels 0-15)
                      in Amperes
        """
        SensorBase.checkPDPChannel(channel)
        return hal.getPDPChannelCurrent(channel)
