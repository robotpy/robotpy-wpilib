# validated: 2018-09-30 EN a818c7fd4741 edu/wpi/first/wpilibj/Watchdog.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .notifier import Notifier
from .timer import Timer

import logging
logger = logging.getLogger('robotpy')


__all__ = ["Watchdog"]


class Watchdog:
    """A class that's a wrapper around a watchdog timer.

    When the timer expires, a message is printed to the console and an optional user-provided
    callback is invoked.

    The watchdog is initialized disabled, so the user needs to call enable() before use.
    """

    def __init__(self, timeout: float, callback=lambda:None) -> None:
        """Watchdog constructor.

        :param timeout: The watchdog's timeout in seconds.
        """
        self.timeout = timeout
        self.callback = callback
        self.startTime = 0.0
        self.epochs = {}
        self._isExpired = False
        self.notifier = Notifier(self.timeoutFunc)
        self.enable()

    def getTime(self) -> float:
        """Get the time in seconds since the watchdog was last fed."""
        return Timer.getFPGATimestamp() - self.startTime

    def isExpired(self) -> bool:
        """Returns true if the watchdog timer has expired."""
        return self._isExpired

    def addEpoch(self, epochName: str) -> None:
        """Adds time since last epoch to the list printed by printEpochs().

        :param epochName: The name to associate with the epoch.
        """
        currentTime = Timer.getFPGATimestamp()
        self.epochs[epochName] = currentTime - self.startTime
        self.startTime = currentTime

    def printEpochs(self) -> None:
        """Prints list of epochs added so far and their times."""
        for key, value in self.epochs.items():
            logger.info("\t%s: %ss" % (key, value))

    def reset(self) -> None:
        """Resets the watchdog timer.

        This also enables the timer if it was previously disabled.
        """
        self.enable()

    def enable(self) -> None:
        """Enables the watchdog timer."""
        self.startTime = Timer.getFPGATimestamp()
        self._isExpired = False
        self.epochs.clear()
        self.notifier.startPeriodic(self.timeout)

    def disable(self) -> None:
        """Disable the watchdog."""
        self.notifier.stop()

    def timeoutFunc(self) -> None:
        if not self._isExpired:
            logger.info("Watchdog not fed after %ss" % (self.timeout,))
            self.callback()
            self._isExpired = True
            self.disable()

