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

class DigitalSource(InterruptableSensorBase):
    """DigitalSource Interface. The DigitalSource represents all the possible
    inputs for a counter or a quadrature encoder. The source may be either a
    digital input or an analog input. If the caller just provides a channel,
    then a digital input will be constructed and freed when finished for the
    source. The source can either be a digital input or analog trigger but
    not both.
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

        self.channel = channel

        # XXX: Replace with hal.checkDigitalChannel when implemented
        SensorBase.checkDigitalChannel(channel)

        try:
            DigitalSource.channels.allocate(self, channel)
        except IndexError as e:
            raise IndexError("Digital input %d is already allocated" % self.channel) from e

        self._port = hal.initializeDigitalPort(hal.getPort(channel))
        hal.allocateDIO(self._port, True if input else False)

        self._port_finalizer = weakref.finalize(self, hal.freeDIO, self._port)

    @property
    def port(self):
        if not self._port_finalizer.alive:
            return None
        return self._port

    def free(self):
        if self.channel is None:
            return
        DigitalSource.channels.free(self.channel)
        self._port_finalizer()
        self.channel = None

    def getChannelForRouting(self):
        """Get the channel routing number

        :returns: channel routing number
        """
        return self.channel

    def getModuleForRouting(self):
        """Get the module routing number

        :returns: 0
        """
        return 0

    def getAnalogTriggerForRouting(self):
        """Is this an analog trigger
        
        :returns: True if this is an analog trigger
        """
        return False
