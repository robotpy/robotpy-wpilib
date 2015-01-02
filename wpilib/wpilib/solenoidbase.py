#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import threading

from .resource import Resource
from .sensorbase import SensorBase

__all__ = ["SolenoidBase"]

class SolenoidBase(SensorBase):
    """SolenoidBase class is the common base class for the Solenoid and
    DoubleSolenoid classes."""

    # global to all instances, keyed by module number
    all_allocated = {}
    all_ports = {}
    all_mutex = {}
    
    @staticmethod
    def _reset():
        SolenoidBase.all_allocated = {}
        SolenoidBase.all_ports = {}
        SolenoidBase.all_mutex = {}

    def __init__(self, moduleNumber):
        """Constructor.

        :param moduleNumber: The PCM CAN ID
        """
        self.moduleNumber = moduleNumber

        if moduleNumber not in self.all_ports:
            self.all_ports[moduleNumber] = []

            for i in range(SensorBase.kSolenoidChannels):
                port = hal.getPortWithModule(moduleNumber, i)
                self.all_ports[moduleNumber].append(hal.initializeSolenoidPort(port))

        if moduleNumber not in self.all_mutex:
            self.all_mutex[moduleNumber] = threading.Lock()

        if moduleNumber not in self.all_allocated:
            self.all_allocated[moduleNumber] = Resource(SensorBase.kSolenoidChannels)

        self.allocated = self.all_allocated[moduleNumber]
        self.ports = self.all_ports[moduleNumber]
        self.mutex = self.all_mutex[moduleNumber]

    def set(self, value, mask):
        """Set the value of a solenoid.

        :param value: The value you want to set on the module.
        :param mask: The channels you want to be affected.
        """
        with self.mutex:
            for i in range(SensorBase.kSolenoidChannels):
                local_mask = 1 << i
                if (mask & local_mask) != 0:
                    hal.setSolenoid(self.ports[i], (value & local_mask) != 0)

    def getAll(self):
        """Read all 8 solenoids from the module used by this solenoid as a
        single byte.

        :returns: The current value of all 8 solenoids on this module.
        """
        with self.mutex:
            value = 0
            for i in range(SensorBase.kSolenoidChannels):
                value |= (1 if hal.getSolenoid(self.ports[i]) else 0) << i
            return value

    def getPCMSolenoidBlackList(self):
        """
        Reads complete solenoid blacklist for all 8 solenoids as a single byte.
            If a solenoid is shorted, it is added to the blacklist and
            disabled until power cycle, or until faults are cleared. See
            :meth:`clearAllPCMStickyFaults`

        :returns: The solenoid blacklist of all 8 solenoids on the module.
        """
        return hal.getPCMSolenoidBlackList(self.ports[0])

    def getPCMSolenoidVoltageStickyFault(self):
        """
        :returns: True if PCM Sticky fault is set : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        return hal.getPCMSolenoidVoltageStickyFault()

    def getPCMSolenoidVoltageFault(self):
        """
        :returns: True if PCM is in fault state : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        return hal.getPCMSolenoidVoltageFault()

    def clearAllPCMStickyFaults(self):
        """
        Clear ALL sticky faults inside the PCM that Solenoid is wired to.

        If a sticky fault is set, then it will be persistently cleared. Compressor drive
            maybe momentarily disable while flages are being cleared. Care should be
            taken to not call this too frequently, otherwise normal compressor functionality
            may be prevented.

        If no sticky faults are set then this call will have no effect.
        """
        hal.clearAllPCMStickyFaults()