# validated: 2016-12-25 JW 963391cf3916 athena/java/edu/wpi/first/wpilibj/DoubleSolenoid.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import warnings

from .livewindow import LiveWindow
from .resource import Resource
from .sensorbase import SensorBase
from .solenoidbase import SolenoidBase

__all__ = ["DoubleSolenoid"]

class DoubleSolenoid(SolenoidBase):
    """Controls 2 channels of high voltage Digital Output on the PCM.

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
        :param forwardChannel: The forward channel number on the module to control (0..7)
        :param reverseChannel: The reverse channel number on the module to control  (0..7)
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
        try:
            self.allocated.allocate(self, forwardChannel)
        except IndexError as e:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (forwardChannel, moduleNumber)) from e
        try:
            self.allocated.allocate(self, reverseChannel)
        except IndexError as e:
            raise IndexError("Solenoid channel %d on module %d is already allocated" % (reverseChannel, moduleNumber)) from e

        portHandle = hal.getPortWithModule(moduleNumber, forwardChannel)
        self.forwardHandle = hal.initializeSolenoidPort(portHandle)
        portHandle = hal.getPortWithModule(moduleNumber, reverseChannel)
        self.reverseHandle = hal.initializeSolenoidPort(portHandle)

        self.forwardChannel = forwardChannel
        self.reverseChannel = reverseChannel
        self.forwardMask = 1 << forwardChannel
        self.reverseMask = 1 << reverseChannel

        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        hal.report(hal.UsageReporting.kResourceType_Solenoid,
                      forwardChannel, moduleNumber)
        hal.report(hal.UsageReporting.kResourceType_Solenoid,
                      reverseChannel, moduleNumber)

        LiveWindow.addActuatorModuleChannel("DoubleSolenoid", moduleNumber,
                                            forwardChannel, self)

    def free(self):
        """Mark the solenoid as freed."""
        LiveWindow.removeComponent(self)
        self.allocated.free(self.forwardChannel)
        self.allocated.free(self.reverseChannel)
        hal.freeSolenoidPort(self.forwardHandle)
        hal.freeSolenoidPort(self.reverseHandle)
        super().free()

    def set(self, value):
        """Set the value of a solenoid.

        :param value: The value to set (Off, Forward, Reverse)
        :type  value: :class:`DoubleSolenoid.Value`
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

    def get(self):
        """Read the current value of the solenoid.

        :returns: The current value of the solenoid.
        :rtype: :class:`DoubleSolenoid.Value`
        """
        if hal.getSolenoid(self.forwardHandle):
            return self.Value.kForward
        if hal.getSolenoid(self.reverseHandle):
            return self.Value.kReverse
        return self.Value.kOff

    def isFwdSolenoidBlackListed(self):
        """
        Check if the forward solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        blacklist = self.getPCMSolenoidBlackList()

        return (blacklist & self.forwardMask) != 0

    def isRevSolenoidBlackListed(self):
        """
        Check if the reverse solenoid is blacklisted.
            If a solenoid is shorted, it is added to the blacklist and disabled until power cycle, or until faults are
            cleared. See :meth:`clearAllPCMStickyFaults`

        :returns: If solenoid is disabled due to short.
        """
        blacklist = self.getPCMSolenoidBlackList()

        return blacklist & (1 << self.reverseMask) != 0

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Double Solenoid"

    def initTable(self, subtable):
        self.table = subtable
        self.updateTable()

    def getTable(self):
        return self.table

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            #TODO: this is bad
            val = self.get()
            if val == self.Value.kForward:
                table.putString("Value", "F")
            elif val == self.Value.kReverse:
                table.putString("Value", "R")
            else:
                table.putString("Value", "O")

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
