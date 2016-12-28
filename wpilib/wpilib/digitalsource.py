# validated: 2016-12-27 JW aafca4ed7fff athena/java/edu/wpi/first/wpilibj/DigitalSource.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .resource import Resource
from .sensorbase import SensorBase
from .interruptablesensorbase import InterruptableSensorBase

__all__ = ["DigitalSource"]

def _freeDigitalSource(handle):
    hal.freeDIOPort(handle)

class DigitalSource(InterruptableSensorBase):
    """DigitalSource Interface. The DigitalSource represents all the possible
    inputs for a counter or a quadrature encoder. The source may be either a
    digital input or an analog input. If the caller just provides a channel,
    then a digital input will be constructed and freed when finished for the
    source. The source can either be a digital input or analog trigger but
    not both.
    
    .. not_implemented: initDigitalPort
    """

    channels = Resource(SensorBase.kDigitalChannels)

    def __init__(self, channel, input):
        """
            :param channel: Port for the digital input
            :type  channel: int
            :param input: True if input, False otherwise
            :type  input: int
        """
        super().__init__()

        SensorBase.checkDigitalChannel(channel)
        self.channel = channel
        self._handle = hal.initializeDIOPort(hal.getPort(channel), input)

        try:
            DigitalSource.channels.allocate(self, channel)
        except IndexError as e:
            raise IndexError("Digital input %d is already allocated" % self.channel) from e

        self.__finalizer = weakref.finalize(self, _freeDigitalSource, self._handle)

    @property
    def handle(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use channel after free() has been called")
        return self._handle

    def free(self):
        DigitalSource.channels.free(self.channel)
        self.__finalizer()

    def isAnalogTrigger(self):
        raise NotImplementedError

    def getChannel(self):
        raise NotImplementedError

