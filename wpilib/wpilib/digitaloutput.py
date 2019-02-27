# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/DigitalOutput.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import warnings
import weakref
from typing import Optional

import hal

from .digitalsource import DigitalSource
from .sensorutil import SensorUtil
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

__all__ = ["DigitalOutput"]


def _freePWMGenerator(pwmGenerator: int) -> None:
    # Disable the output by routing to a dead bit.
    hal.setDigitalPWMOutputChannel(pwmGenerator, SensorUtil.kDigitalChannels)
    hal.freeDigitalPWM(pwmGenerator)


class DigitalOutput(SendableBase):
    """Writes to a digital output
    
    Other devices that are implemented elsewhere will automatically allocate
    digital inputs and outputs as required.
    """

    invalidPwmGenerator = None

    def __init__(self, channel: int) -> None:
        """Create an instance of a digital output.

        :param channel: the DIO channel for the digital output. 0-9 are on-board, 10-25 are on the MXP
        """

        super().__init__()
        self.pwmGenerator = None
        self._pwmGenerator_finalizer = None

        SensorUtil.checkDigitalChannel(channel)
        self.channel = channel

        self.handle = hal.initializeDIOPort(hal.getPort(channel), False)

        hal.report(hal.UsageReporting.kResourceType_DigitalOutput, channel)
        self.setName("DigitalOutput", channel)

    def close(self) -> None:
        """Free the resources associated with a digital output."""
        super().close()
        # finalize the pwm only if we have allocated it
        if self.pwmGenerator is not None:
            self._pwmGenerator_finalizer()
        self.pwmGenerator = None
        if self.pwmGenerator is not self.invalidPwmGenerator:
            self.disablePWM()
        hal.freeDIOPort(self.handle)
        self.handle = 0

    def set(self, value: bool) -> None:
        """Set the value of a digital output.

        :param value: True is on, off is False
        """
        hal.setDIO(self.handle, bool(value))

    def get(self) -> bool:
        """Gets the value being output from the Digital Output.

        :returns: the state of the digital output
        """
        return hal.getDIO(self.handle)

    def getChannel(self) -> int:
        """:returns: The GPIO channel number that this object represents.
        """
        return self.channel

    def pulse(self, pulseLength: float) -> None:
        """Generate a single pulse. There can only be a single pulse going at any time.

        :param pulseLength: The length of the pulse.
        """
        hal.pulse(self.handle, pulseLength)

    def isPulsing(self) -> bool:
        """Determine if the pulse is still going. Determine if a previously
        started pulse is still going.

        :returns: True if pulsing
        """
        return hal.isPulsing(self.handle)

    def setPWMRate(self, rate: float) -> None:
        """Change the PWM frequency of the PWM output on a Digital Output line.

        The valid range is from 0.6 Hz to 19 kHz. The frequency resolution is
        logarithmic.

        There is only one PWM frequency for all channels.

        :param rate: The frequency to output all digital output PWM signals.
        """
        hal.setDigitalPWMRate(rate)

    def enablePWM(self, initialDutyCycle: float) -> None:
        """Enable a PWM Output on this line.

        Allocate one of the 6 DO PWM generator resources.

        Supply the initial duty-cycle to output so as to avoid a glitch when
        first starting.

        The resolution of the duty cycle is 8-bit for low frequencies (1kHz or
        less) but is reduced the higher the frequency of the PWM signal is.

        :param initialDutyCycle: The duty-cycle to start generating. [0..1]
        """
        if self.pwmGenerator is not self.invalidPwmGenerator:
            return
        self.pwmGenerator = hal.allocateDigitalPWM()
        hal.setDigitalPWMDutyCycle(self.pwmGenerator, initialDutyCycle)
        hal.setDigitalPWMOutputChannel(self.pwmGenerator, self.channel)
        self._pwmGenerator_finalizer = weakref.finalize(
            self, _freePWMGenerator, self.pwmGenerator
        )

    def disablePWM(self) -> None:
        """Change this line from a PWM output back to a static Digital Output
        line.

        Free up one of the 6 DO PWM generator resources that were in use.
        """
        if self.pwmGenerator is not self.invalidPwmGenerator:
            return
        hal.setDigitalPWMOutputChannel(self.pwmGenerator, SensorUtil.kDigitalChannels)
        hal.freeDigitalPWM(self.pwmGenerator)
        self._pwmGenerator_finalizer()

    def updateDutyCycle(self, dutyCycle: float) -> None:
        """Change the duty-cycle that is being generated on the line.

        The resolution of the duty cycle is 8-bit for low frequencies (1kHz or
        less) but is reduced the higher the frequency of the PWM signal is.

        :param dutyCycle: The duty-cycle to change to. [0..1]
        """
        if self.pwmGenerator is self.invalidPwmGenerator:
            return
        hal.setDigitalPWMDutyCycle(self.pwmGenerator, dutyCycle)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Digital Output")
        builder.addBooleanProperty("Value", self.get, self.set)
