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

    def __init__(self, moduleNumber):
        """Constructor.

        :param moduleNumber: The number of the solenoid module to use.
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
