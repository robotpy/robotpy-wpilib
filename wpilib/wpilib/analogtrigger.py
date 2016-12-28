# validated: 2016-12-03 TW e44a6e227a89 athena/java/edu/wpi/first/wpilibj/AnalogTrigger.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .analoginput import AnalogInput
from .analogtriggeroutput import AnalogTriggerOutput
from .resource import Resource

__all__ = ["AnalogTrigger"]

def _freeAnalogTrigger(port):
    hal.cleanAnalogTrigger(port)

class AnalogTrigger:
    """
        Converts an analog signal into a digital signal
        
        An analog trigger is a way to convert an analog signal into a digital
        signal using resources built into the FPGA. The resulting digital
        signal can then be used directly or fed into other digital components
        of the FPGA such as the counter or encoder modules. The analog trigger
        module works by comparing analog signals to a voltage range set by
        the code. The specific return types and meanings depend on the analog
        trigger mode in use.
        
        .. not_implemented: initTrigger
    """

    AnalogTriggerType = AnalogTriggerOutput.AnalogTriggerType

    def __init__(self, channel):
        """Constructor for an analog trigger given a channel number or analog
        input.

        :param channel: the port index or :class:`.AnalogInput` to use for the analog
            trigger.  Treated as an AnalogInput if the provided object has a
            getChannel function.
        """
        if hasattr(channel, "getChannel"):
            self.analogInput = channel
        else:
            self.analogInput = AnalogInput(channel)

        port = hal.getPort(channel)
        self._port, self.index = hal.initializeAnalogTrigger(port)
        self.__finalizer = \
                weakref.finalize(self, _freeAnalogTrigger, self._port)
                
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        hal.report(hal.UsageReporting.kResourceType_AnalogTrigger,
                      channel)

    @property
    def port(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use AnalogTrigger after free() has been called")
        return self._port

    def free(self):
        """Release the resources used by this object"""
        self.__finalizer()
        if self.analogInput:
            self.analogInput.free()
            

    def setLimitsRaw(self, lower, upper):
        """Set the upper and lower limits of the analog trigger. The limits are
        given in ADC codes. If oversampling is used, the units must be scaled
        appropriately.

        :param lower: the lower raw limit
        :param upper: the upper raw limit
        """
        if lower > upper:
            raise ValueError("Lower bound is greater than upper")
        
        hal.setAnalogTriggerLimitsRaw(self.port, lower, upper)

    def setLimitsVoltage(self, lower, upper):
        """Set the upper and lower limits of the analog trigger. The limits are
        given as floating point voltage values.

        :param lower: the lower voltage limit
        :param upper: the upper voltage limit
        """
        if lower > upper:
            raise ValueError("Lower bound is greater than upper")
        
        hal.setAnalogTriggerLimitsVoltage(self.port, float(lower), float(upper))

    def setAveraged(self, useAveragedValue):
        """Configure the analog trigger to use the averaged vs. raw values. If
        the value is true, then the averaged value is selected for the analog
        trigger, otherwise the immediate value is used.

        :param useAveragedValue: True to use an averaged value, False otherwise
        """
        hal.setAnalogTriggerAveraged(self.port, useAveragedValue)

    def setFiltered(self, useFilteredValue):
        """Configure the analog trigger to use a filtered value. The analog
        trigger will operate with a 3 point average rejection filter. This is
        designed to help with 360 degree pot applications for the period where
        the pot crosses through zero.

        :param useFilteredValue: True to use a filterd value, False otherwise
        """
        hal.setAnalogTriggerFiltered(self.port, useFilteredValue)

    def getIndex(self):
        """Return the index of the analog trigger. This is the FPGA index of
        this analog trigger instance.

        :returns: The index of the analog trigger.
        """
        return self.index

    def getInWindow(self):
        """Return the InWindow output of the analog trigger. True if the
        analog input is between the upper and lower limits.

        :returns: The InWindow output of the analog trigger.
        """
        return hal.getAnalogTriggerInWindow(self.port)

    def getTriggerState(self):
        """Return the TriggerState output of the analog trigger. True if above
        upper limit. False if below lower limit. If in Hysteresis, maintain
        previous state.

        :returns: The TriggerState output of the analog trigger.
        """
        return hal.getAnalogTriggerTriggerState(self.port)

    def createOutput(self, type):
        """Creates an :class:`.AnalogTriggerOutput` object. Gets an output object that
        can be used for routing. Caller is responsible for deleting the
        AnalogTriggerOutput object.

        :param type: An enum of the type of output object to create.
        :returns: An AnalogTriggerOutput object.
        """
        return AnalogTriggerOutput(self, type)
