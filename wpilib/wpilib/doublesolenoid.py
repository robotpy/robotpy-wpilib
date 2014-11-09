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

__all__ = ["DoubleSolenoid"]

class DoubleSolenoid(SolenoidBase):
    """DoubleSolenoid class for running 2 channels of high voltage Digital
    Output.

    The DoubleSolenoid class is typically used for pneumatics solenoids that
    have two positions controlled by two separate channels.
    """

    class Value:
        """Possible values for a DoubleSolenoid."""
        kOff = 0
        kForward = 1
        kReverse = 2

    def __init__(self, *args, **kwargs):
        """Constructor.

        Arguments can be supplied as positional or keyword.  Acceptable
        positional argument combinations are:
        
        - forwardChannel, reverseChannel
        - moduleNumber, forwardChannel, reverseChannel

        Alternatively, the above names can be used as keyword arguments.

        :param moduleNumber: The module number of the solenoid module to use.
        :param forwardChannel: The forward channel on the module to control.
        :param reverseChannel: The reverse channel on the module to control.
        """
        # keyword arguments
        forwardChannel = kwargs.pop("forwardChannel", None)
        reverseChannel = kwargs.pop("reverseChannel", None)
        moduleNumber = kwargs.pop("moduleNumber", None)

        if kwargs:
            warnings.warn("unknown keyword arguments: %s" % kwargs.keys(),
                          RuntimeWarning)

        # positional arguments
        if len(args) == 2:
            forwardChannel, reverseChannel = args
        elif len(args) == 3:
            moduleNumber, forwardChannel, reverseChannel = args
        elif len(args) != 0:
            raise ValueError("don't know how to handle %d positional arguments" % len(args))

        if moduleNumber is None:
            moduleNumber = SensorBase.getDefaultSolenoidModule()
        if forwardChannel is None:
            raise ValueError("must specify forward channel")
        if reverseChannel is None:
            raise ValueError("must specify reverse channel")

        SensorBase.checkSolenoidModule(moduleNumber)
        SensorBase.checkSolenoidChannel(forwardChannel)
        SensorBase.checkSolenoidChannel(reverseChannel)

        super().__init__(moduleNumber)
        self.forwardChannel = forwardChannel
        self.reverseChannel = reverseChannel

        try:
            self.allocated.allocate(self, forwardChannel)
        except IndexError:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (forwardChannel, moduleNumber))
        try:
            self.allocated.allocate(self, reverseChannel)
        except IndexError:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (reverseChannel, moduleNumber))

        self.forwardPort = self.ports[forwardChannel]
        self.reversePort = self.ports[reverseChannel]

        hal.HALReport(hal.HALUsageReporting.kResourceType_Solenoid,
                      forwardChannel, moduleNumber)
        hal.HALReport(hal.HALUsageReporting.kResourceType_Solenoid,
                      reverseChannel, moduleNumber)

        LiveWindow.addActuatorModuleChannel("DoubleSolenoid", moduleNumber,
                                            forwardChannel, self)

    def free(self):
        """Mark the solenoid as freed."""
        self.allocated.free(self.forwardChannel)
        self.allocated.free(self.reverseChannel)

    def set(self, value):
        """Set the value of a solenoid.

        :param value: Move the solenoid to forward, reverse, or don't move it.
        """
        rawValue = 0

        if value == self.Value.kOff:
            hal.setSolenoid(self.forwardPort, False)
            hal.setSolenoid(self.reversePort, False)
        elif value == self.Value.kForward:
            hal.setSolenoid(self.reversePort, False)
            hal.setSolenoid(self.forwardPort, True)
        elif value == self.Value.kReverse:
            hal.setSolenoid(self.forwardPort, False)
            hal.setSolenoid(self.reversePort, True)

    def get(self):
        """Read the current value of the solenoid.

        :returns: The current value of the solenoid.
        """
        if hal.getSolenoid(self.forwardPort):
            return self.Value.kForward
        if hal.getSolenoid(self.reversePort):
            return self.Value.kReverse
        return Value.kOff

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Double Solenoid"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            #TODO: this is bad
            val = self.get()
            if val == self.Value.kForward:
                table.putString("Value", "Forward")
            elif value == self.Value.kReverse:
                table.putString("Value", "Reverse")
            else:
                table.putString("Value", "Off")

    def valueChanged(self, itable, key, value, bln):
        #TODO: this is bad also
        if value == "Reverse":
            self.set(self.Value.kReverse)
        elif value == "Forward":
            self.set(self.Value.kForward)
        else:
            self.set(self.Value.kOff)

    def startLiveWindowMode(self):
        self.set(self.Value.kOff) # Stop for safety
        super().startLiveWindowMode()

    def stopLiveWindowMode(self):
        super().stopLiveWindowMode()
        self.set(self.Value.kOff) # Stop for safety
