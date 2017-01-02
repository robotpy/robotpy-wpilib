# validated: 2016-12-31 JW 8f67f2c24cb9 athena/java/edu/wpi/first/wpilibj/DigitalOutput.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import warnings
import weakref

import hal

from .digitalsource import DigitalSource
from .sensorbase import SensorBase

__all__ = ["DigitalOutput"]

def _freePWMGenerator(pwmGenerator):
    # Disable the output by routing to a dead bit.
    hal.setDigitalPWMOutputChannel(pwmGenerator, SensorBase.kDigitalChannels)
    hal.freeDigitalPWM(pwmGenerator)

class DigitalOutput(DigitalSource):
    """Writes to a digital output
    
    Other devices that are implemented elsewhere will automatically allocate
    digital inputs and outputs as required.
    """

    def __init__(self, channel):
        """Create an instance of a digital output.

        :param channel: the DIO channel for the digital output. 0-9 are on-board, 10-25 are on the MXP
        """
        super().__init__(channel, False)
        self._pwmGenerator = None
        self._pwmGenerator_finalizer = None

        hal.report(hal.UsageReporting.kResourceType_DigitalOutput,
                      channel)

    @property
    def pwmGenerator(self):
        if self._pwmGenerator_finalizer is None:
            return None
        if not self._pwmGenerator_finalizer.alive:
            return None
        return self._pwmGenerator

    def free(self):
        """Free the resources associated with a digital output."""
        # finalize the pwm only if we have allocated it
        if self.pwmGenerator is not None:
            self._pwmGenerator_finalizer()
        self._pwmGenerator = None
        super().free()
        self._handle = None

    def set(self, value):
        """Set the value of a digital output.

        :param value: True is on, off is False
        :type  value: bool
        """
        hal.setDIO(self.port, 1 if value else 0)

    def get(self):
        """Gets the value being output from the Digital Output.

        :returns: the state of the digital output
        :rtype: bool
        """
        return hal.getDIO(self.handle)

    def getChannel(self):
        """:returns: The GPIO channel number that this object represents.
        """
        return self.channel

    def pulse(self, pulseLength, *args):
        """Generate a single pulse. There can only be a single pulse going at any time.

        :param channel: Unused. Deprecated 2017.1.1.
        :param pulseLength: The length of the pulse.
        :type  pulseLength: float
        """
        if len(args) > 0:
            warnings.warn("Use of channel argument is deprecated.", DeprecationWarning)
            pulseLength = args[0]
        hal.pulse(self.handle, pulseLength)

    def isPulsing(self):
        """Determine if the pulse is still going. Determine if a previously
        started pulse is still going.

        :returns: True if pulsing
        :rtype: bool
        """
        return hal.isPulsing(self.handle)

    def setPWMRate(self, rate):
        """Change the PWM frequency of the PWM output on a Digital Output line.

        The valid range is from 0.6 Hz to 19 kHz. The frequency resolution is
        logarithmic.

        There is only one PWM frequency for all channnels.

        :param rate: The frequency to output all digital output PWM signals.
        :type  rate: float
        """
        hal.setDigitalPWMRate(rate)

    def enablePWM(self, initialDutyCycle):
        """Enable a PWM Output on this line.

        Allocate one of the 6 DO PWM generator resources.

        Supply the initial duty-cycle to output so as to avoid a glitch when
        first starting.

        The resolution of the duty cycle is 8-bit for low frequencies (1kHz or
        less) but is reduced the higher the frequency of the PWM signal is.

        :param initialDutyCycle: The duty-cycle to start generating. [0..1]
        :type  initialDutyCycle: float
        """
        if self.pwmGenerator is not None:
            return
        self._pwmGenerator = hal.allocateDigitalPWM()
        hal.setDigitalPWMDutyCycle(self._pwmGenerator, initialDutyCycle)
        hal.setDigitalPWMOutputChannel(self._pwmGenerator, self.channel)
        self._pwmGenerator_finalizer = \
                weakref.finalize(self, _freePWMGenerator, self._pwmGenerator)

    def disablePWM(self):
        """Change this line from a PWM output back to a static Digital Output
        line.

        Free up one of the 6 DO PWM generator resources that were in use.
        """
        if self.pwmGenerator is None:
            return
        self._pwmGenerator_finalizer()

    def updateDutyCycle(self, dutyCycle):
        """Change the duty-cycle that is being generated on the line.

        The resolution of the duty cycle is 8-bit for low frequencies (1kHz or
        less) but is reduced the higher the frequency of the PWM signal is.

        :param dutyCycle: The duty-cycle to change to. [0..1]
        :type  dutyCycle: float
        """
        if self.pwmGenerator is None:
            return
        hal.setDigitalPWMDutyCycle(self.pwmGenerator, dutyCycle)

    def getAnalogTriggerTypeForRouting(self):
        """Get the analog trigger type.

        :returns: false
        :rtype: int
        """
        return 0

    def isAnalogTrigger(self):
        """Is this an analog trigger.

        :returns: true if this is an analog trigger
        :rtype: bool
        """
        return False

    def getPortHandleForRouting(self):
        """Get the HAL Port Handle.

        :returns: The HAL Handle to the specified source
        """
        return self.handle

    def initTable(self, subtable):
        self.table = subtable
        self.updateTable()

    # Live Window code, only does anything if live window is activated.
    def getSmartDashboardType(self):
        return "Digital Output"

    def updateTable(self):
        # TODO: Put current value.
        pass

    def valueChanged(self, itable, key, value, bln):
        self.set(True if value else False)
