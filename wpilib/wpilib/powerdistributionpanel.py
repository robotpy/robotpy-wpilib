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
    """Use to obtain voltage, current, temperature, power, and energy from the CAN PDP
    
    The PDP must be at CAN Address 0
    """

    def getVoltage(self):
        """
            Query the voltage of the PDP

            :returns: The voltage of the PDP in volts
            :rtype: float
        """
        return hal.getPDPVoltage()

    def getTemperature(self):
        """
            Query the temperature of the PDP

            :returns: The temperature of the PDP in degrees Celsius
            :rtype: float
        """
        return hal.getPDPTemperature()

    def getCurrent(self, channel):
        """
            Query the current of a single channel of the PDP

            :returns: The current of one of the PDP channels (channels 0-15)
                      in Amperes
            :rtype: float
        """
        SensorBase.checkPDPChannel(channel)
        return hal.getPDPChannelCurrent(channel)
    
    def getTotalCurrent(self):
        """
            Query the current of all monitored PDP channels (0-15)

            :returns: The total current drawn from the PDP channels in Amperes
            :rtype: float
        """
        return hal.getPDPTotalCurrent()
    
    def getTotalPower(self):
        """
            Query the total power drawn from the monitored PDP channels

            :returns: The total power drawn from the PDP channels in Watts
            :rtype: float
        """
        return hal.getPDPTotalPower()
    
    def getTotalEnergy(self):
        """
            Query the total energy drawn from the monitored PDP channels

            :returns: The total energy drawn from the PDP channels in Joules
            :rtype: float
        """
        return hal.getPDPTotalEnergy()
    
    def resetTotalEnergy(self):
        """
            Reset the total energy to 0
        """
        hal.resetPDPTotalEnergy()
    
    def clearStickyFaults(self):
        """
            Clear all pdp sticky faults
        """
        hal.clearPDPStickyFaults()

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "PowerDistributionPanel"

    def initTable(self, subtable):
        self.table = subtable
        self.updateTable()

    def getTable(self):
        return self.table

    def updateTable(self):
        if self.table is not None:
            for channel in range(0, 15):
                self.table.putNumber("Chan" + str(channel), self.getCurrent(channel))
            self.table.putNumber("Voltage", self.getVoltage())
            self.table.putNumber("Current", self.getTotalCurrent())

    def startLiveWindowMode(self):
        """
        PDP doesn't have to do anything special when entering the LiveWindow.
        """
        pass

    def stopLiveWindowMode(self):
        """
        PDP doesn't have to do anything special when exiting the LiveWindow.
        """
        pass