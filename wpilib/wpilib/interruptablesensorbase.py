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

__all__ = ["InterruptableSensorBase"]

class InterruptableSensorBase(SensorBase):
    """Base for sensors to be used with interrupts"""

    # Resource manager
    interrupts = Resource(8)

    def __init__(self):
        """Create a new InterrupatableSensorBase"""
        # The interrupt resource
        self._interrupt = None
        self._interrupt_finalizer = None
        # Flags if the interrupt being allocated is synchronous
        self.isSynchronousInterrupt = False
        # The index of the interrupt
        self.interruptIndex = None

    def getAnalogTriggerForRouting(self):
        raise NotImplementedError

    def getChannelForRouting(self):
        raise NotImplementedError

    def getModuleForRouting(self):
        raise NotImplementedError

    @property
    def interrupt(self):
        if self._interrupt_finalizer is None:
            return None
        if not self._interrupt_finalizer.alive:
            return None
        return self._interrupt

    def requestInterrupts(self, handler=None):
        """Request one of the 8 interrupts asynchronously on this digital
        input.

        :param handler: (optional)
            The function that will be called whenever there is an interrupt
            on this device.  Request interrupts in synchronous mode where the
            user program interrupt handler will be called when an interrupt
            occurs. The default is interrupt on rising edges only.  If not
            specified, the user program will have to explicitly wait for the
            interrupt to occur using waitForInterrupt.
        """
        if self.interrupt is not None:
            raise ValueError("The interrupt has already been allocated")

        self.allocateInterrupts(handler is not None)

        assert self.interrupt is not None

        hal.requestInterrupts(self.interrupt, self.getModuleForRouting(),
                              self.getChannelForRouting(),
                              1 if self.getAnalogTriggerForRouting() else 0)
        self.setUpSourceEdge(True, False)
        if handler is not None:
            hal.attachInterruptHandler(self.interrupt, handler)

    def allocateInterrupts(self, watcher):
        """Allocate the interrupt

        :param watcher: True if the interrupt should be in synchronous mode
            where the user program will have to explicitly wait for the interrupt
            to occur.
        """
        if self.interrupt is not None:
            raise ValueError("The interrupt has already been allocated")

        try:
            self.interruptIndex = \
                    InterruptableSensorBase.interrupts.allocate(self)
        except IndexError as e:
            raise IndexError("No interrupts are left to be allocated") from e

        self.isSynchronousInterrupt = watcher
        self._interrupt = hal.initializeInterrupts(self.interruptIndex,
                                                   1 if watcher else 0)
        self._interrupt_finalizer = weakref.finalize(self, hal.cleanInterrupts,
                                                     self._interrupt)

    def cancelInterrupts(self):
        """Cancel interrupts on this device. This deallocates all the
        chipobject structures and disables any interrupts.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        self._interrupt_finalizer()
        InterruptableSensorBase.interrupts.free(self.interruptIndex)
        self.interruptIndex = None

    def waitForInterrupt(self, timeout, ignorePrevious=True):
        """In synchronous mode, wait for the defined interrupt to occur.
        You should **NOT** attempt to read the sensor from another thread
        while waiting for an interrupt. This is not threadsafe, and can cause 
        memory corruption

        :param timeout: Timeout in seconds
        :param ignorePrevious: If True (default), ignore interrupts that
            happened before waitForInterrupt was called.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.waitForInterrupt(self.interrupt, timeout, ignorePrevious)

    def enableInterrupts(self):
        """Enable interrupts to occur on this input. Interrupts are disabled
        when the RequestInterrupt call is made. This gives time to do the
        setup of the other options before starting to field interrupts.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise ValueError("You do not need to enable synchronous interrupts")
        hal.enableInterrupts(self.interrupt)

    def disableInterrupts(self):
        """Disable Interrupts without without deallocating structures."""
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise ValueError("You can not disable synchronous interrupts")
        hal.disableInterrupts(self.interrupt)

    def readRisingTimestamp(self):
        """Return the timestamp for the rising interrupt that occurred most
        recently.  This is in the same time domain as getClock().  The
        rising-edge interrupt should be enabled with setUpSourceEdge.

        :returns: Timestamp in seconds since boot.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.readRisingTimestamp(self.interrupt)

    def readFallingTimestamp(self):
        """Return the timestamp for the falling interrupt that occurred most
        recently.  This is in the same time domain as getClock().  The
        falling-edge interrupt should be enabled with setUpSourceEdge.

        :returns: Timestamp in seconds since boot.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.readFallingTimestamp(self.interrupt)

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
            raise ValueError("You must call RequestInterrupts before setUpSourceEdge")
