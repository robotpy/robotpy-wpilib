#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .analogtriggeroutput import AnalogTriggerOutput

__all__ = ["AnalogTrigger"]

def _freeAnalogTrigger(port):
    hal.cleanAnalogTrigger(port)

class AnalogTrigger:
    """Class for creating and configuring Analog Triggers"""

    AnalogTriggerType = AnalogTriggerOutput.AnalogTriggerType

    def __init__(self, channel):
        """Constructor for an analog trigger given a channel number or analog
        input.

        :param channel: the port index or `AnalogInput` to use for the analog
            trigger.  Treated as an AnalogInput if the provided object has a
            getChannel function.
        """
        if hasattr(channel, "getChannel"):
            channel = channel.getChannel()

        port = hal.getPort(channel)
        self._port, self.index = hal.initializeAnalogTrigger(port)
        self._analogtrigger_finalizer = \
                weakref.finalize(self, _freeAnalogTrigger, self._port)

        hal.HALReport(hal.HALUsageReporting.kResourceType_AnalogTrigger,
                      channel)

    @property
    def port(self):
        if not self._analogtrigger_finalizer.alive:
            return None
        return self._analogtrigger

    def free(self):
        """Release the resources used by this object"""
        self._analogtrigger_finalizer()

    def setLimitsRaw(self, lower, upper):
        """Set the upper and lower limits of the analog trigger. The limits are
        given in ADC codes. If oversampling is used, the units must be scaled
        appropriately.

        :param lower: the lower raw limit
        :param upper: the upper raw limit
        """
        if lower > upper:
            raise ValueError("Lower bound is greater than upper")
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setAnalogTriggerLimitsRaw(self.port, lower, upper)

    def setLimitsVoltage(self, lower, upper):
        """Set the upper and lower limits of the analog trigger. The limits are
        given as floating point voltage values.

        :param lower: the lower voltage limit
        :param upper: the upper voltage limit
        """
        if lower > upper:
            raise ValueError("Lower bound is greater than upper")
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setAnalogTriggerLimitsVoltage(self.port, float(lower), float(upper))

    def setAveraged(self, useAveragedValue):
        """Configure the analog trigger to use the averaged vs. raw values. If
        the value is true, then the averaged value is selected for the analog
        trigger, otherwise the immediate value is used.

        :param useAveragedValue: True to use an averaged value, False otherwise
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setAnalogTriggerAveraged(self.port, useAveragedValue)

    def setFiltered(self, useFilteredValue):
        """Configure the analog trigger to use a filtered value. The analog
        trigger will operate with a 3 point average rejection filter. This is
        designed to help with 360 degree pot applications for the period where
        the pot crosses through zero.

        :param useFilteredValue: True to use a filterd value, False otherwise
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setAnalogTriggerFiltered(self.port, useFilteredValue)

    def getIndex(self):
        """Return the index of the analog trigger. This is the FPGA index of
        this analog trigger instance.

        :returns: The index of the analog trigger.
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return self.index

    def getInWindow(self):
        """Return the InWindow output of the analog trigger. True if the
        analog input is between the upper and lower limits.

        :returns: The InWindow output of the analog trigger.
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return hal.getAnalogTriggerInWindow(self.port)

    def getTriggerState(self):
        """Return the TriggerState output of the analog trigger. True if above
        upper limit. False if below lower limit. If in Hysteresis, maintain
        previous state.

        :returns: The TriggerState output of the analog trigger.
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return hal.getAnalogTriggerTriggerState(self.port)

    def createOutput(self, type):
        """Creates an AnalogTriggerOutput object. Gets an output object that
        can be used for routing. Caller is responsible for deleting the
        AnalogTriggerOutput object.

        :param type: An enum of the type of output object to create.
        :returns: An AnalogTriggerOutput object.
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return AnalogTriggerOutput(self, type)
