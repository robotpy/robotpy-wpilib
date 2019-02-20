# validated: 2019-02-02 DV 43696956d20b edu/wpi/first/wpilibj/Watchdog.java
# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import heapq
import threading
from typing import Callable, Dict, List

import hal

import logging

logger = logging.getLogger(__name__)


__all__ = ["Watchdog"]


class Watchdog:
    """A class that's a wrapper around a watchdog timer.

    When the timer expires, a message is printed to the console and an optional user-provided
    callback is invoked.

    The watchdog is initialized disabled, so the user needs to call enable() before use.
    """

    # Used for timeout print rate-limiting
    kMinPrintPeriod = 1000000  # us

    _watchdogs = []  # type: List[Watchdog]
    _queueMutex = threading.Lock()
    _schedulerWaiter = threading.Condition(_queueMutex)
    _keepAlive = True
    _thread = None

    @classmethod
    def _reset(cls) -> None:
        with cls._queueMutex:
            thread = cls._thread
        if thread is not None:
            cls._keepAlive = False
            with cls._queueMutex:
                cls._watchdogs.clear()
                cls._schedulerWaiter.notify_all()
                cls._thread = None
            thread.join()
        cls._keepAlive = True

    def __init__(self, timeout: float, callback: Callable[[], None]) -> None:
        """Watchdog constructor.

        :param timeout: The watchdog's timeout in seconds with microsecond resolution.
        :param callback: This function is called when the timeout expires.
        """
        self._startTime = 0  # us
        self._timeout = int(timeout * 1e6)  # us
        self._expirationTime = 0  # us
        self._callback = callback
        self._lastTimeoutPrintTime = 0  # us
        self._lastEpochsPrintTime = 0  # us
        self._epochs = {}  # type: Dict[str, int]
        self._isExpired = False

        #: Enable or disable suppression of the generic timeout message.
        #:
        #: This may be desirable if the user-provided callback already
        #: prints a more specific message.
        self.suppressTimeoutMessage = False

        with self._queueMutex:
            if Watchdog._thread is None:
                Watchdog._thread = threading.Thread(
                    target=Watchdog._schedulerFunc, daemon=True
                )
                Watchdog._thread.start()

    # Elements with sooner expiration times are sorted as lesser.
    # Python's heap queue is a min-heap.

    def __lt__(self, other: "Watchdog") -> bool:
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self._expirationTime < other._expirationTime

    def __eq__(self, other) -> bool:
        return (
            self.__class__ is other.__class__
            and self._expirationTime == other._expirationTime
        )

    def __gt__(self, other: "Watchdog") -> bool:
        if self.__class__ is not other.__class__:
            return NotImplemented
        return self._expirationTime > other._expirationTime

    def getTime(self) -> float:
        """Returns the time in seconds since the watchdog was last fed."""
        return (hal.getFPGATime() - self._startTime) / 1e6

    def setTimeout(self, timeout: float) -> None:
        """Sets the watchdog's timeout.

        :param timeout: The watchdog's timeout in seconds with microsecond
                        resolution.
        """
        self._startTime = hal.getFPGATime()
        self._epochs.clear()
        timeout = int(timeout * 1e6)  # us

        with self._queueMutex:
            self._timeout = timeout
            self._isExpired = False

            watchdogs = self._watchdogs
            try:
                watchdogs.remove(self)
            except ValueError:
                pass
            else:
                heapq.heapify(watchdogs)

            self._expirationTime = self._startTime + timeout
            heapq.heappush(watchdogs, self)
            self._schedulerWaiter.notify_all()

    def getTimeout(self) -> float:
        """Returns the watchdog's timeout in seconds."""
        with self._queueMutex:
            return self._timeout / 1e6

    def isExpired(self) -> bool:
        """Returns true if the watchdog timer has expired."""
        with self._queueMutex:
            return self._isExpired

    def addEpoch(self, epochName: str) -> None:
        """
        Adds time since last epoch to the list printed by printEpochs().

        Epochs are a way to partition the time elapsed so that when
        overruns occur, one can determine which parts of an operation
        consumed the most time.

        :param epochName: The name to associate with the epoch.
        """
        currentTime = hal.getFPGATime()
        self._epochs[epochName] = currentTime - self._startTime
        self._startTime = currentTime

    def printEpochs(self) -> None:
        """Prints list of epochs added so far and their times."""
        now = hal.getFPGATime()
        if now - self._lastEpochsPrintTime > self.kMinPrintPeriod:
            self._lastEpochsPrintTime = now
            log = logger.info
            for key, value in self._epochs.items():
                log("\t%s: %.6fs", key, value / 1e6)

    def reset(self) -> None:
        """Resets the watchdog timer.

        This also enables the timer if it was previously disabled.
        """
        self.enable()

    def enable(self) -> None:
        """Enables the watchdog timer."""
        self._startTime = hal.getFPGATime()
        self._epochs.clear()

        with self._queueMutex:
            self._isExpired = False

            watchdogs = self._watchdogs
            try:
                watchdogs.remove(self)
            except ValueError:
                pass
            else:
                heapq.heapify(watchdogs)

            self._expirationTime = self._startTime + self._timeout
            heapq.heappush(watchdogs, self)
            self._schedulerWaiter.notify_all()

    def disable(self) -> None:
        """Disables the watchdog timer."""
        with self._queueMutex:
            watchdogs = self._watchdogs
            try:
                watchdogs.remove(self)
            except ValueError:
                pass
            else:
                heapq.heapify(watchdogs)
            self._schedulerWaiter.notify_all()

    @classmethod
    def _schedulerFunc(cls) -> None:
        # Grab a bunch of things before the loop to avoid some lookups.
        getFPGATime = hal.getFPGATime
        heappop = heapq.heappop
        log = logger.info
        lock = cls._queueMutex
        watchdogs = cls._watchdogs
        cond = cls._schedulerWaiter

        with lock:
            # Python-specific: need a way to terminate the thread.
            while cls._keepAlive:
                if watchdogs:
                    delta = watchdogs[0]._expirationTime - getFPGATime()
                    timedOut = not cond.wait(delta / 1e6)

                    if timedOut:
                        if (
                            not watchdogs
                            or watchdogs[0]._expirationTime > getFPGATime()
                        ):
                            continue

                        # If the condition variable timed out, that means a Watchdog
                        # timeout has occurred, so call its timeout function.
                        watchdog = heappop(watchdogs)

                        now = getFPGATime()
                        if now - watchdog._lastTimeoutPrintTime > cls.kMinPrintPeriod:
                            watchdog._lastTimeoutPrintTime = now
                            if not watchdog.suppressTimeoutMessage:
                                log(
                                    "Watchdog not fed after %.6fs",
                                    watchdog._timeout / 1e6,
                                )

                        # Set expiration flag before calling the callback so any
                        # manipulation of the flag in the callback (e.g. calling
                        # Disable()) isn't clobbered.
                        watchdog._isExpired = True

                        lock.release()
                        try:
                            watchdog._callback()
                        except Exception:
                            logger.exception("Uncaught exception in Watchdog callback")
                        lock.acquire()

                    # Otherwise, a Watchdog removed itself from the queue (it
                    # notifies the scheduler of this), we are being reset (by
                    # the test harness) or a spurious wakeup occurred, so rewait
                    # with the soonest watchdog timeout.
                else:
                    while cls._keepAlive and not watchdogs:
                        cond.wait()
