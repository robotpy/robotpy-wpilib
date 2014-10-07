#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .sensorbase import SensorBase
from .solenoidbase import SolenoidBase

class Solenoid(SolenoidBase):
    """Solenoid class for running high voltage Digital Output.

    The Solenoid class is typically used for pneumatics solenoids, but could
    be used for any device within the current spec of the PCM.
    """

    def __init__(self, *args, **kwargs):
        """Constructor.

        Arguments can be supplied as positional or keyword.  Acceptable
        positional argument combinations are:
        - channel
        - moduleNumber, channel

        Alternatively, the above names can be used as keyword arguments.

        :param moduleNumber: The module number of the solenoid module to use.
        :param channel: The channel on the module to control.
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
        except IndexError:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (channel, moduleNumber))

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
        """
        with self.mutex:
            hal.setSolenoid(self.port, on)

    def get(self):
        """Read the current value of the solenoid.

        :returns: The current value of the solenoid.
        """
        with self.mutex:
            return hal.getSolenoid(self.port)

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Solenoid"

    def initTable(self, subtable):
        self.table = subtable
        self.updateTable()

    def getTable(self):
        return getattr(self, "table", None)

    def updateTable(self):
        table = getattr(self, "table", None)
        if table is not None:
            table.putBoolean("Value", self.get())

    def startLiveWindowMode(self):
        table = getattr(self, "table", None)
        table_listener = getattr(self, "table_listener", None)
        if table is None or table_listener is not None:
            return

        def valueChanged(itable, key, value, bln):
            self.set(bool(value))

        self.set(False) # Stop for safety
        self.table_listener = valueChanged
        self.table.addTableListener("Value", valueChanged, True)

    def stopLiveWindowMode(self):
        # TODO: Broken, should only remove the listener from "Value" only.
        table = getattr(self, "table", None)
        table_listener = getattr(self, "table_listener", None)
        if table is None or table_listener is None:
            return

        self.set(False) # Stop for safety
        table.removeTableListener(table_listener)
        self.table_listener = None
