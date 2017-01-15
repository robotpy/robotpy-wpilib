# validated: 2016-12-25 JW 963391cf3916 athena/java/edu/wpi/first/wpilibj/SolenoidBase.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .sensorbase import SensorBase

__all__ = ["SolenoidBase"]

class SolenoidBase(SensorBase):
    """SolenoidBase class is the common base class for the Solenoid and
    DoubleSolenoid classes."""

    def __init__(self, moduleNumber):
        """Constructor.

        :param moduleNumber: The PCM CAN ID
        """
        self.moduleNumber = moduleNumber

    def getAll(self):
        """Read all 8 solenoids from the module used by this solenoid as a
        single byte.

        :returns: The current value of all 8 solenoids on this module.
        """
        return hal.getAllSolenoids(self.moduleNumber)

    def getPCMSolenoidBlackList(self):
        """
        Reads complete solenoid blacklist for all 8 solenoids as a single byte.
            If a solenoid is shorted, it is added to the blacklist and
            disabled until power cycle, or until faults are cleared. See
            :meth:`clearAllPCMStickyFaults`

        :returns: The solenoid blacklist of all 8 solenoids on the module.
        """
        return hal.getPCMSolenoidBlackList(self.moduleNumber)

    def getPCMSolenoidVoltageStickyFault(self):
        """
        :returns: True if PCM Sticky fault is set : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        return hal.getPCMSolenoidVoltageStickyFault(self.moduleNumber)

    def getPCMSolenoidVoltageFault(self):
        """
        :returns: True if PCM is in fault state : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        return hal.getPCMSolenoidVoltageFault(self.moduleNumber)

    def clearAllPCMStickyFaults(self):
        """
        Clear ALL sticky faults inside the PCM that Solenoid is wired to.

        If a sticky fault is set, then it will be persistently cleared. Compressor drive
            maybe momentarily disable while flages are being cleared. Care should be
            taken to not call this too frequently, otherwise normal compressor functionality
            may be prevented.

        If no sticky faults are set then this call will have no effect.
        """
        hal.clearAllPCMStickyFaults(self.moduleNumber)

