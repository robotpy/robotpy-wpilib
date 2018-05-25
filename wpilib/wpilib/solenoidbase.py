# validated: 2017-12-12 EN f9bece2ffbf7 edu/wpi/first/wpilibj/SolenoidBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Union

import hal

from .sendablebase import SendableBase

__all__ = ["SolenoidBase"]


class SolenoidBase(SendableBase):
    """SolenoidBase class is the common base class for the Solenoid and
    DoubleSolenoid classes."""

    def __init__(self, moduleNumber: int) -> None:
        """Constructor.

        :param moduleNumber: The PCM CAN ID
        """
        super().__init__()
        self.moduleNumber = moduleNumber

    def getAll(moduleNumber: Union[int, "SolenoidBase"]) -> int:
        """Read all 8 solenoids from the specified module as a
        single byte.

        :param moduleNumber: in a static context, the module number to read. otherwise don't provide it.
        :returns: The current value of all 8 solenoids on the module.
        """
        if isinstance(moduleNumber, SolenoidBase):
            moduleNumber = moduleNumber.moduleNumber
        return hal.getAllSolenoids(moduleNumber)

    def getPCMSolenoidBlackList(moduleNumber: Union[int, "SolenoidBase"]) -> int:
        """
        Reads complete solenoid blacklist for all 8 solenoids as a single byte.
            If a solenoid is shorted, it is added to the blacklist and
            disabled until power cycle, or until faults are cleared. See
            :meth:`clearAllPCMStickyFaults`

        :param moduleNumber: in a static context, the module number to read. otherwise don't provide it.
        :returns: The solenoid blacklist of all 8 solenoids on the module.
        """
        if isinstance(moduleNumber, SolenoidBase):
            moduleNumber = moduleNumber.moduleNumber
        return hal.getPCMSolenoidBlackList(moduleNumber)

    def getPCMSolenoidVoltageStickyFault(
        moduleNumber: Union[int, "SolenoidBase"]
    ) -> bool:
        """
        :param moduleNumber: in a static context, the module number to read. otherwise don't provide it.
        :returns: True if PCM Sticky fault is set : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        if isinstance(moduleNumber, SolenoidBase):
            moduleNumber = moduleNumber.moduleNumber
        return hal.getPCMSolenoidVoltageStickyFault(moduleNumber)

    def getPCMSolenoidVoltageFault(moduleNumber: Union[int, "SolenoidBase"]) -> bool:
        """
        :param moduleNumber: in a static context, the module number to read. otherwise don't provide it.
        :returns: True if PCM is in fault state : The common
            highside solenoid voltage rail is too low, most likely
            a solenoid channel has been shorted.
        """
        if isinstance(moduleNumber, SolenoidBase):
            moduleNumber = moduleNumber.moduleNumber
        return hal.getPCMSolenoidVoltageFault(moduleNumber)

    def clearAllPCMStickyFaults(moduleNumber: Union[int, "SolenoidBase"]) -> None:
        """
        Clear ALL sticky faults inside the PCM that Solenoid is wired to.

        If a sticky fault is set, then it will be persistently cleared. Compressor drive
            maybe momentarily disable while flages are being cleared. Care should be
            taken to not call this too frequently, otherwise normal compressor functionality
            may be prevented.

        If no sticky faults are set then this call will have no effect.

        :param moduleNumber: in a static context, the module number to read. otherwise don't provide it.
        """
        if isinstance(moduleNumber, SolenoidBase):
            moduleNumber = moduleNumber.moduleNumber
        hal.clearAllPCMStickyFaults(moduleNumber)
