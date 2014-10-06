#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .resource import Resource
from .sensorbase import SensorBase

class InterruptableSensorBase(SensorBase):
    """Base for sensors to be used with interrupts"""

    # Resource manager
    interrupts = Resource(8)

    def __init__(self):
        """Create a new InterrupatableSensorBase"""
        # The interrupt resource
        self.interrupt = None
        # Flags if the interrupt being allocated is synchronous
        self.isSynchronousInterrupt = False
        # The index of the interrupt
        self.interruptIndex = 0

    def __del__(self):
        if self.interrupt is not None:
            self.cancelInterrupts()

    def getAnalogTriggerForRouting(self):
        raise NotImplementedError

    def getChannelForRouting(self):
        raise NotImplementedError

    def getModuleForRouting(self):
        raise NotImplementedError

    def requestInterrupts(self, handler):
        """Request interrupts asynchronously on this digital input.

        :param handler:
            The function that will be called whenever there is an interrupt
            on this device.  Request interrupts in synchronus mode where the
            user program interrupt handler will be called when an interrupt
            occurs. The default is interrupt on rising edges only.
        """
        if self.interrupt is not None:
            raise RuntimeError("The interrupt has already been allocated")

        self.allocateInterrupts(False)

        assert self.interrupt is not None

        hal.requestInterrupts(self.interrupt, self.getModuleForRouting(),
                              self.getChannelForRouting(),
                              1 if self.getAnalogTriggerForRouting() else 0)
        self.setUpSourceEdge(True, False)
        hal.attachInterruptHandler(self.interrupt, handler)

    def requestInterrupts(self):
        """Request interrupts synchronously on this digital input. Request
        interrupts in synchronous mode where the user program will have to
        explicitly wait for the interrupt to occur. The default is interrupt
        on rising edges only.
        """
        if self.interrupt is not None:
            raise RuntimeError("The interrupt has already been allocated")

        self.allocateInterrupts(True)

        assert self.interrupt is not None

        hal.requestInterrupts(self.interrupt, self.getModuleForRouting(),
                              self.getChannelForRouting(),
                              1 if self.getAnalogTriggerForRouting() else 0)
        self.setUpSourceEdge(True, False)

    def allocateInterrupts(self, watcher):
        """Allocate the interrupt

        :param watcher: True if the interrupt should be in synchronous mode
        where the user program will have to explicitly wait for the interrupt
        to occur.
        """
        try:
            self.interruptIndex = InterruptibleSensorBase.interrupts.allocate()
        except IndexError:
            raise IndexError("No interrupts are left to be allocated")

        self.isSynchronousInterrupt = watcher
        self.interrupt = hal.initializeInterrupts(self.interruptIndex,
                                                  1 if watcher else 0)

    def cancelInterrupts(self):
        """Cancel interrupts on this device. This deallocates all the
        chipobject structures and disables any interrupts.
        """
        if self.interrupt is None:
            raise RuntimeError("The interrupt is not allocated.")
        hal.cleanInterrupts(self.interrupt)
        self.interrupt = None
        InterruptibleSensorBase.interrupts.free(self.interruptIndex)

    def waitForInterrupt(self, timeout):
        """In synchronous mode, wait for the defined interrupt to occur.

        :param timeout: Timeout in seconds
        """
        if self.interrupt is None:
            raise RuntimeError("The interrupt is not allocated.")
        hal.waitForInterrupt(self.interrupt, timeout)

    def enableInterrupts(self):
        """Enable interrupts to occur on this input. Interrupts are disabled
        when the RequestInterrupt call is made. This gives time to do the
        setup of the other options before starting to field interrupts.
        """
        if self.interrupt is None:
            raise RuntimeError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise RuntimeError("You do not need to enable synchronous interrupts")
        hal.enableInterrupts(self.interrupt)

    def disableInterrupts(self):
        """Disable Interrupts without without deallocating structures."""
        if self.interrupt is None:
            raise RuntimeError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise RuntimeError("You can not disable synchronous interrupts")
        hal.disableInterrupts(self.interrupt)

    def readInterruptTimestamp(self):
        """Return the timestamp for the interrupt that occurred most recently.
        This is in the same time domain as getClock().

        :returns: Timestamp in seconds since boot.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.readInterruptTimestamp(self.interrupt)

    def setUpSourceEdge(self, risingEdge, fallingEdge):
        """Set which edge to trigger interrupts on

        :param risingEdge: True to interrupt on rising edge
        :param fallingEdge: True to interrupt on falling edge
        """
        if self.interrupt is not None:
            hal.setInterruptUpSourceEdge(self.interrupt,
                                         1 if risingEdge else 0,
                                         1 if fallingEdge else 0)
        else:
            raise RuntimeError("You must call RequestInterrupts before setUpSourceEdge")
