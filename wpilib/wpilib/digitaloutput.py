#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import weakref

import hal

from .digitalsource import DigitalSource
from .sensorbase import SensorBase

__all__ = ["DigitalOutput"]

def _freePWMGenerator(pwmGenerator):
    # Disable the output by routing to a dead bit.
    hal.setPWMOutputChannel(pwmGenerator, SensorBase.kDigitalChannels)
    hal.freePWM(pwmGenerator)

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

        hal.HALReport(hal.HALUsageReporting.kResourceType_DigitalOutput,
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
        super().free()

    def set(self, value):
        """Set the value of a digital output.

        :param value: True is on, off is False
        :type  value: bool
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setDIO(self.port, 1 if value else 0)

    def getChannel(self):
        """:returns: The GPIO channel number that this object represents.
        """
        return self.channel

    def pulse(self, channel, pulseLength):
        """Generate a single pulse. Write a pulse to the specified digital
        output channel. There can only be a single pulse going at any time.

        :param channel: The channel to pulse.
        :param pulseLength: The length of the pulse.
        :type  pulseLength: float
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.pulse(self.port, pulseLength)

    def isPulsing(self):
        """Determine if the pulse is still going. Determine if a previously
        started pulse is still going.

        :returns: True if pulsing
        :rtype: bool
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return hal.isPulsing(self.port)

    def setPWMRate(self, rate):
        """Change the PWM frequency of the PWM output on a Digital Output line.

        The valid range is from 0.6 Hz to 19 kHz. The frequency resolution is
        logarithmic.

        There is only one PWM frequency for all channnels.

        :param rate: The frequency to output all digital output PWM signals.
        :type  rate: float
        """
        hal.setPWMRate(rate)

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
        self._pwmGenerator = hal.allocatePWM()
        hal.setPWMDutyCycle(self._pwmGenerator, initialDutyCycle)
        hal.setPWMOutputChannel(self._pwmGenerator, self.channel)
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
        hal.setPWMDutyCycle(self.pwmGenerator, dutyCycle)

    # Live Window code, only does anything if live window is activated.
    def getSmartDashboardType(self):
        return "Digital Output"

    def updateTable(self):
        # TODO: Put current value.
        pass

    def valueChanged(self, itable, key, value, bln):
        self.set(True if value else False)
