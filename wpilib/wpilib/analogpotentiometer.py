# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/AnalogPotentiometer.java
# ----------------------------------------------------------------------------*/
# Copyright (c) FIRST 2008-2017. All Rights Reserved.                        */
# Open Source Software - may be modified and shared by FRC teams. The code   */
# must be accompanied by the FIRST BSD license file in the root directory of */
# the project.                                                               */
# ----------------------------------------------------------------------------*/
from typing import Union

import hal

from .analoginput import AnalogInput
from .interfaces import PIDSource
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

__all__ = ["AnalogPotentiometer"]


class AnalogPotentiometer(SendableBase):
    """Reads a potentiometer via an :class:`.AnalogInput`
    
    Analog potentiometers read
    in an analog voltage that corresponds to a position. The position is in
    whichever units you choose, by way of the scaling and offset constants
    passed to the constructor.

    .. not_implemented: initPot
    """

    PIDSourceType = PIDSource.PIDSourceType

    def __init__(
        self,
        channel: Union[AnalogInput, int],
        fullRange: float = 1.0,
        offset: float = 0.0,
    ) -> None:
        """AnalogPotentiometer constructor.

        Use the fullRange and offset values so that the output produces
        meaningful values. I.E: you have a 270 degree potentiometer and
        you want the output to be degrees with the halfway point as 0
        degrees. The fullRange value is 270.0(degrees) and the offset is
        -135.0 since the halfway point after scaling is 135 degrees.

        :param channel: The analog channel this potentiometer is plugged into.
        :param fullRange: The scaling to multiply the fraction by to get a
            meaningful unit.  Defaults to 1.0 if unspecified.
        :param offset: The offset to add to the scaled value for controlling
            the zero value.  Defaults to 0.0 if unspecified.
        """

        super().__init__()
        if not hasattr(channel, "getVoltage"):
            channel = AnalogInput(channel)
            self.addChild(channel)
        self.analog_input = channel
        self.fullRange = fullRange
        self.offset = offset
        self.init_analog_input = True
        self.pidSource = self.PIDSourceType.kDisplacement
        self.setName("AnalogPotentiometer", self.analog_input.getChannel())

    def get(self) -> float:
        """Get the current reading of the potentiometer.

        :returns: The current position of the potentiometer.
        """
        if self.analog_input is None:
            return self.offset
        return (
            self.analog_input.getVoltage() / hal.getUserVoltage5V()
        ) * self.fullRange + self.offset

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """Set which parameter you are using as a process
        control variable. 

        :param pidSource: An enum to select the parameter.
        """
        if pidSource != self.PIDSourceType.kDisplacement:
            raise ValueError("Only displacement PID is allowed for potentiometers.")
        self.pidSource = pidSource

    def getPIDSourceType(self) -> PIDSourceType:
        return self.pidSource

    def pidGet(self) -> float:
        """Implement the PIDSource interface.

        :returns: The current reading.
        """
        return self.get()

    def initSendable(self, builder: SendableBuilder) -> None:
        if self.analog_input is not None:
            self.analog_input.initSendable(builder)

    def close(self) -> None:
        super().close()

        if self.init_analog_input:
            self.analog_input.close()
            del self.analog_input
            self.init_analog_input = False
