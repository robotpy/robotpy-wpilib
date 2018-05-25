# validated: 2018-09-09 EN 0614913f1abb edu/wpi/first/wpilibj/DoubleSolenoid.java
# ----------------------------------------------------------------------------
# Copyright (c) 2008-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import enum
import warnings
import weakref

from .resource import Resource
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder
from .solenoidbase import SolenoidBase

__all__ = ["DoubleSolenoid"]


def _freeSolenoid(fwdHandle: hal.SolenoidHandle, revHandle: hal.SolenoidHandle) -> None:
    hal.freeSolenoidPort(fwdHandle)
    hal.freeSolenoidPort(revHandle)


class DoubleSolenoid(SolenoidBase):
    """Controls 2 channels of high voltage Digital Output on the PCM.

    The DoubleSolenoid class is typically used for pneumatics solenoids that
    have two positions controlled by two separate channels.
    """

    class Value(enum.IntEnum):
        """Possible values for a DoubleSolenoid."""

        kOff = 0
        kForward = 1
        kReverse = 2

    def __init__(self, *args, **kwargs) -> None:
        """Constructor.

        Arguments can be supplied as positional or keyword.  Acceptable
        positional argument combinations are:
        
        - forwardChannel, reverseChannel
        - moduleNumber, forwardChannel, reverseChannel

        Alternatively, the above names can be used as keyword arguments.

        :param moduleNumber: The module number of the solenoid module to use.
        :param forwardChannel: The forward channel number on the module to control (0..7)
        :param reverseChannel: The reverse channel number on the module to control  (0..7)
        """
        # keyword arguments
        forwardChannel = kwargs.pop("forwardChannel", None)
        reverseChannel = kwargs.pop("reverseChannel", None)
        moduleNumber = kwargs.pop("moduleNumber", None)

        if kwargs:
            warnings.warn(
                "unknown keyword arguments: %s" % kwargs.keys(), RuntimeWarning
            )

        # positional arguments
        if len(args) == 2:
            forwardChannel, reverseChannel = args
        elif len(args) == 3:
            moduleNumber, forwardChannel, reverseChannel = args
        elif len(args) != 0:
            raise ValueError(
                "don't know how to handle %d positional arguments" % len(args)
            )

        if moduleNumber is None:
            moduleNumber = SensorUtil.getDefaultSolenoidModule()
        if forwardChannel is None:
            raise ValueError("must specify forward channel")
        if reverseChannel is None:
            raise ValueError("must specify reverse channel")

        super().__init__(moduleNumber)

        self.valueEntry = None
        SensorUtil.checkSolenoidModule(moduleNumber)
        SensorUtil.checkSolenoidChannel(forwardChannel)
        SensorUtil.checkSolenoidChannel(reverseChannel)

        portHandle = hal.getPortWithModule(moduleNumber, forwardChannel)
        self.forwardHandle = hal.initializeSolenoidPort(portHandle)

        try:
            portHandle = hal.getPortWithModule(moduleNumber, reverseChannel)
            self.reverseHandle = hal.initializeSolenoidPort(portHandle)
        except Exception:
            # free the forward handle on exception, then rethrow
            hal.freeSolenoidPort(self.forwardHandle)
            self.forwardHandle = None
            self.reverseHandle = None
            raise

        self.forwardMask = 1 << forwardChannel
        self.reverseMask = 1 << reverseChannel

        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        hal.report(
            hal.UsageReporting.kResourceType_Solenoid, forwardChannel, moduleNumber
        )
        hal.report(
            hal.UsageReporting.kResourceType_Solenoid, reverseChannel, moduleNumber
        )

        self.setName("DoubleSolenoid", moduleNumber, forwardChannel)

        self.__finalizer = weakref.finalize(
            self, _freeSolenoid, self.forwardHandle, self.reverseHandle
        )

    def close(self) -> None:
        """Mark the solenoid as freed."""
        super().close()
        self.__finalizer()
        self.forwardHandle = None
        self.reverseHandle = None

    def set(self, value: Value) -> None:
        """Set the value of a solenoid.

        :param value: The value to set (Off, Forward, Reverse)
        """

        if value == self.Value.kOff:
            hal.setSolenoid(self.forwardHandle, False)
            hal.setSolenoid(self.reverseHandle, False)
        elif value == self.Value.kForward:
            hal.setSolenoid(self.reverseHandle, False)
            hal.setSolenoid(self.forwardHandle, True)
        elif value == self.Value.kReverse:
            hal.setSolenoid(self.forwardHandle, False)
            hal.setSolenoid(self.reverseHandle, True)
        else:
            raise ValueError("Invalid argument '%s'" % value)

    def get(self) -> Value:
        """Read the current value of the solenoid.

        :returns: The current value of the solenoid.
        """
        if hal.getSolenoid(self.forwardHandle):
            return self.Value.kForward
        if hal.getSolenoid(self.reverseHandle):
            return self.Value.kReverse
        return self.Value.kOff

    def isFwdSolenoidBlackListed(self) -> bool:
        """
        Check if the forward solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        blacklist = self.getPCMSolenoidBlackList()

        return (blacklist & self.forwardMask) != 0

    def isRevSolenoidBlackListed(self) -> bool:
        """
        Check if the reverse solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        blacklist = self.getPCMSolenoidBlackList()

        return blacklist & (1 << self.reverseMask) != 0

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Double Solenoid")
        builder.setActuator(True)
        builder.setSafeState(lambda: self.set(self.Value.kOff))
        builder.addStringProperty(
            "Value", lambda: self.get().name[1:], self._valueChanged
        )

    def _valueChanged(self, value: str) -> None:
        if value == "Reverse":
            self.set(self.Value.kReverse)
        elif value == "Forward":
            self.set(self.Value.kForward)
        else:
            self.set(self.Value.kOff)
