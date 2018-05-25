# validated: 2017-11-23 TW e1195e8b9dab edu/wpi/first/wpilibj/DigitalSource.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal
import weakref

from .resource import Resource
from .interruptablesensorbase import InterruptableSensorBase

__all__ = ["DigitalSource"]


def _freeDigitalSource(handle: hal.DigitalHandle) -> None:
    hal.freeDIOPort(handle)


class DigitalSource(InterruptableSensorBase):
    """DigitalSource Interface. The DigitalSource represents all the possible
    inputs for a counter or a quadrature encoder. The source may be either a
    digital input or an analog input. If the caller just provides a channel,
    then a digital input will be constructed and freed when finished for the
    source. The source can either be a digital input or analog trigger but
    not both.
    """

    def isAnalogTrigger(self) -> bool:
        raise NotImplementedError

    def getChannel(self) -> int:
        raise NotImplementedError
