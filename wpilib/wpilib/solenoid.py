#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import warnings

from .livewindow import LiveWindow
from .sensorbase import SensorBase
from .solenoidbase import SolenoidBase

__all__ = ["Solenoid"]

class Solenoid(SolenoidBase):
    """Solenoid class for running high voltage Digital Output.

    The Solenoid class is typically used for pneumatics solenoids, but could
    be used for any device within the current spec of the PCM.
    
    .. not_implemented: initSolenoid
    """

    def __init__(self, *args, **kwargs):
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
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 1:
            channel = args[0]
        elif len(args) == 2:
            moduleNumber, channel = args
        elif len(args) != 0:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        if moduleNumber is None:
            moduleNumber = SensorBase.getDefaultSolenoidModule()
        if channel is None:
            raise ValueError("must specify channel")

        SensorBase.checkSolenoidModule(moduleNumber)
        SensorBase.checkSolenoidChannel(channel)

        super().__init__(moduleNumber)
        self.channel = channel

        try:
            self.allocated.allocate(self, channel)
        except IndexError as e:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (channel, moduleNumber)) from e

        self.port = self.ports[channel]

        LiveWindow.addActuatorModuleChannel("Solenoid", moduleNumber, channel,
                                            self)
        hal.HALReport(hal.HALUsageReporting.kResourceType_Solenoid, channel,
                      moduleNumber)

    def free(self):
        """Mark the solenoid as freed."""
        self.allocated.free(self.channel)

    def set(self, on):
        """Set the value of a solenoid.

        :param on: Turn the solenoid output off or on.
        :type on: bool
        """
        with self.mutex:
            hal.setSolenoid(self.port, on)

    def get(self):
        """Read the current value of the solenoid.

        :returns: The current value of the solenoid.
        :rtype: bool
        """
        with self.mutex:
            return hal.getSolenoid(self.port)

    def isBlackListed(self):
        """
        Check if the solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        value = self.getPCMSolenoidBlackList() & (1 << self.channel)
        return value != 0

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Solenoid"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putBoolean("Value", self.get())

    def valueChanged(self, itable, key, value, bln):
        self.set(True if value else False)

    def startLiveWindowMode(self):
        self.set(False) # Stop for safety
        super().startLiveWindowMode()

    def stopLiveWindowMode(self):
        super().stopLiveWindowMode()
        self.set(False) # Stop for safety
