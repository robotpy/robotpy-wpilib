# validated: 2018-12-18 n 9207d788ab50 edu/wpi/first/wpilibj/InterruptableSensorBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Callable, Optional
import enum
import weakref

import hal
from .sendablebase import SendableBase

__all__ = ["InterruptableSensorBase"]


class InterruptableSensorBase(SendableBase):
    """Base for sensors to be used with interrupts"""

    class WaitResult(enum.IntEnum):
        kTimeout = 0x0
        kRisingEdge = 0x1
        kFallingEdge = 0x100
        kBoth = 0x101

    def __init__(self) -> None:
        """Create a new InterrupatableSensorBase"""
        super().__init__()
        # The interrupt resource
        self.interrupt = None
        self._interrupt_finalizer = None
        # Flags if the interrupt being allocated is synchronous
        self.isSynchronousInterrupt = False

    def close(self) -> None:
        super().close()
        if self.interrupt is not None:
            self.cancelInterrupts()

    def getAnalogTriggerTypeForRouting(self) -> int:
        raise NotImplementedError

    def getPortHandleForRouting(self) -> int:
        raise NotImplementedError

    def requestInterrupts(
        self, handler: Optional[Callable[[int], None]] = None
    ) -> None:
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
        if self.interrupt:
            raise ValueError("The interrupt has already been allocated")

        self.allocateInterrupts(handler is not None)

        assert self.interrupt is not None

        hal.requestInterrupts(
            self.interrupt,
            self.getPortHandleForRouting(),
            self.getAnalogTriggerTypeForRouting(),
        )
        self.setUpSourceEdge(True, False)

    def allocateInterrupts(self, watcher: bool) -> None:
        """Allocate the interrupt

        :param watcher: True if the interrupt should be in synchronous mode
            where the user program will have to explicitly wait for the interrupt
            to occur.
        """
        if self.interrupt is not None:
            raise ValueError("The interrupt has already been allocated")
        self.isSynchronousInterrupt = watcher
        self.interrupt = hal.initializeInterrupts(watcher)
        self._interrupt_finalizer = weakref.finalize(
            self, hal.cleanInterrupts, self.interrupt
        )

    def cancelInterrupts(self) -> None:
        """Cancel interrupts on this device. This deallocates all the
        chipobject structures and disables any interrupts.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        self._interrupt_finalizer()
        hal.cleanInterrupts(self.interrupt)
        self.interrupt = None

    def waitForInterrupt(self, timeout: float, ignorePrevious: bool = True) -> int:
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
        result = hal.waitForInterrupt(self.interrupt, timeout, ignorePrevious)
        rising = 0x1 if (result & 0xFF) else 0x0
        falling = 0x100 if (result & 0xFF00) else 0x0

        result = rising | falling
        return self.WaitResult(result)

    def enableInterrupts(self) -> None:
        """Enable interrupts to occur on this input. Interrupts are disabled
        when the RequestInterrupt call is made. This gives time to do the
        setup of the other options before starting to field interrupts.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise ValueError("You do not need to enable synchronous interrupts")
        hal.enableInterrupts(self.interrupt)

    def disableInterrupts(self) -> None:
        """Disable Interrupts without without deallocating structures."""
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        if self.isSynchronousInterrupt:
            raise ValueError("You can not disable synchronous interrupts")
        hal.disableInterrupts(self.interrupt)

    def readRisingTimestamp(self) -> float:
        """Return the timestamp for the rising interrupt that occurred most
        recently.  This is in the same time domain as getClock().  The
        rising-edge interrupt should be enabled with setUpSourceEdge.

        :returns: Timestamp in seconds since boot.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.readInterruptRisingTimestamp(self.interrupt) * 1e-6

    def readFallingTimestamp(self) -> float:
        """Return the timestamp for the falling interrupt that occurred most
        recently.  This is in the same time domain as getClock().  The
        falling-edge interrupt should be enabled with setUpSourceEdge.

        :returns: Timestamp in seconds since boot.
        """
        if self.interrupt is None:
            raise ValueError("The interrupt is not allocated.")
        return hal.readInterruptFallingTimestamp(self.interrupt) * 1e-6

    def setUpSourceEdge(self, risingEdge: bool, fallingEdge: bool) -> None:
        """Set which edge to trigger interrupts on

        :param risingEdge: True to interrupt on rising edge
        :param fallingEdge: True to interrupt on falling edge
        """
        if self.interrupt is not None:
            hal.setInterruptUpSourceEdge(
                self.interrupt, 1 if risingEdge else 0, 1 if fallingEdge else 0
            )
        else:
            raise ValueError("You must call RequestInterrupts before setUpSourceEdge")
