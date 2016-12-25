# validated: 2016-12-21 JW 8cec94869980 athena/java/edu/wpi/first/wpilibj/AnalogTriggerOutput.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .digitalsource import DigitalSource

__all__ = ["AnalogTriggerOutput"]

class AnalogTriggerOutput(DigitalSource):
    """Represents a specific output from an :class:`.AnalogTrigger`
    
    This class is used to get the current output value and also as a
    :class:`.DigitalSource` to provide routing of an output to digital
    subsystems on the FPGA such as :class:`.Counter`, :class:`.Encoder:,
    and :class:`.Interrupt`.

    The TriggerState output indicates the primary output value of the trigger.
    If the analog signal is less than the lower limit, the output is False. If
    the analog value is greater than the upper limit, then the output is True.
    If the analog value is in between, then the trigger output state maintains
    its most recent value.

    The InWindow output indicates whether or not the analog signal is inside
    the range defined by the limits.

    The RisingPulse and FallingPulse outputs detect an instantaneous transition
    from above the upper limit to below the lower limit, and vise versa. These
    pulses represent a rollover condition of a sensor and can be routed to an
    up / down couter or to interrupts. Because the outputs generate a pulse,
    they cannot be read directly. To help ensure that a rollover condition is
    not missed, there is an average rejection filter available that operates on
    the upper 8 bits of a 12 bit number and selects the nearest outlyer of 3
    samples.  This will reject a sample that is (due to averaging or sampling)
    errantly between the two limits. This filter will fail if more than one
    sample in a row is errantly in between the two limits. You may see this
    problem if attempting to use this feature with a mechanical rollover
    sensor, such as a 360 degree no-stop potentiometer without signal
    conditioning, because the rollover transition is not sharp / clean enough.
    Using the averaging engine may help with this, but rotational speeds of the
    sensor will then be limited.
    """

    def __init__(self, trigger, outputType):
        """Create an object that represents one of the four outputs from an
        analog trigger.

        Because this class derives from DigitalSource, it can be passed into
        routing functions for Counter, Encoder, etc.

        :param trigger: The trigger for which this is an output.
        :param outputType: An enum that specifies the output on the trigger
            to represent.
        """
        self.trigger = trigger
        self.outputType = outputType

        hal.report(hal.UsageReporting.kResourceType_AnalogTriggerOutput,
                      trigger.index, outputType)

    def free(self):
        if self.interrupt is not None:
            self.cancelInterrupts()

    def get(self):
        """Get the state of the analog trigger output.

        :returns: The state of the analog trigger output.
        :rtype: :class:`.AnalogTriggerType`
        """
        return hal.getAnalogTriggerOutput(self.trigger.port, self.outputType)

    def getPortHandleForRouting(self):
        return self.trigger.port

    def getChannel(self):
        return self.trigger.index

    def getAnalogTriggerTypeForRouting(self):
        return self.outputType

    class AnalogTriggerType:
        """Defines the state in which the :class:`.AnalogTrigger` triggers"""
        kInWindow = hal.AnalogTriggerType.kInWindow
        kState = hal.AnalogTriggerType.kState
        kRisingPulse = hal.AnalogTriggerType.kRisingPulse
        kFallingPulse = hal.AnalogTriggerType.kFallingPulse
