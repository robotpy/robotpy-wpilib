# validated: 2018-09-09 EN 0614913f1abb edu/wpi/first/wpilibj/Solenoid.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import weakref
import warnings

from .sendablebuilder import SendableBuilder

from .livewindow import LiveWindow
from .resource import Resource
from .sensorutil import SensorUtil
from .solenoidbase import SolenoidBase

__all__ = ["Solenoid"]


def _freeSolenoid(solenoidHandle: hal.SolenoidHandle) -> None:
    hal.freeSolenoidPort(solenoidHandle)


class Solenoid(SolenoidBase):
    """Solenoid class for running high voltage Digital Output.

    The Solenoid class is typically used for pneumatic solenoids, but could
    be used for any device within the current spec of the PCM.
    
    .. not_implemented: initSolenoid
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor.

        Arguments can be supplied as positional or keyword.  Acceptable
        positional argument combinations are:
        
        - channel
        - moduleNumber, channel

        Alternatively, the above names can be used as keyword arguments.

        :param moduleNumber: The CAN ID of the PCM the solenoid is attached to
        :type moduleNumber: int
        :param channel: The channel on the PCM to control (0..7)
        :type channel: int
        """
        # keyword arguments
        channel = kwargs.pop("channel", None)
        moduleNumber = kwargs.pop("moduleNumber", None)

        if kwargs:
            warnings.warn(
                "unknown keyword arguments: %s" % kwargs.keys(), RuntimeWarning
            )

        # positional arguments
        if len(args) == 1:
            channel = args[0]
        elif len(args) == 2:
            moduleNumber, channel = args
        elif len(args) != 0:
            raise ValueError(
                "don't know how to handle %d positional arguments" % len(args)
            )

        if moduleNumber is None:
            moduleNumber = SensorUtil.getDefaultSolenoidModule()
        if channel is None:
            raise ValueError("must specify channel")

        super().__init__(moduleNumber)
        self.channel = channel

        SensorUtil.checkSolenoidModule(moduleNumber)
        SensorUtil.checkSolenoidChannel(channel)

        portHandle = hal.getPortWithModule(moduleNumber, channel)
        self.solenoidHandle = hal.initializeSolenoidPort(portHandle)

        hal.report(hal.UsageReporting.kResourceType_Solenoid, channel, moduleNumber)
        self.setName("Solenoid", self.moduleNumber, self.channel)

        self.__finalizer = weakref.finalize(self, _freeSolenoid, self.solenoidHandle)

        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

    def close(self) -> None:
        """Mark the solenoid as close."""
        super().close()

        self.__finalizer()
        self.solenoidHandle = None

    def set(self, on: bool) -> None:
        """Set the value of a solenoid.

        :param on: True will turn the solenoid output on. False will turn the solenoid output off.
        """
        hal.setSolenoid(self.solenoidHandle, on)

    def get(self) -> bool:
        """Read the current value of the solenoid.

        :returns: True if the solenoid output is on or false if the solenoid output is off.
        """
        return hal.getSolenoid(self.solenoidHandle)

    def isBlackListed(self) -> bool:
        """
        Check if the solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`.SolenoidBase.clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        value = self.getPCMSolenoidBlackList() & (1 << self.channel)
        return value != 0

    def setPulseDuration(self, durationSeconds: float) -> None:
        """
        Set the pulse duration in the PCM. This is used in conjunction with
        the startPulse method to allow the PCM to control the timing of a pulse.
        The timing can be controlled in 0.01 second increments.

        see :meth:`startPulse`

        :param durationSeconds: The duration of the pulse, from 0.01 to 2.55 seconds.
        """
        duration_ms = int(durationSeconds * 1000)
        hal.setOneShotDuration(self.solenoidHandle, duration_ms)

    def startPulse(self) -> None:
        """
        Trigger the PCM to generate a pulse of the duration set in
        setPulseDuration.

        see :meth:`setPulseDuration`
        """
        hal.fireOneShot(self.solenoidHandle)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Solenoid")
        builder.setActuator(True)
        builder.setSafeState(lambda: self.set(False))
        builder.addBooleanProperty("Value", self.get, self.set)
