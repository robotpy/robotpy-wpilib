# validated: 2018-11-08 EN e2100730447d edu/wpi/first/wpilibj/Notifier.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import threading

import hal

from .resource import Resource
from .robotcontroller import RobotController


class Notifier:
    def __init__(self, run: callable) -> None:
        """
        Create a Notifier for timer event notification.

        :param run: The handler that is called at the notification time which is
                    set using :meth:`.startSingle` or :meth:`.startPeriodic`.
        """
        #: The lock for the process information.
        self._processLock = threading.RLock()

        # Notifier handle
        self._notifier = hal.initializeNotifier()

        #: The time, in microseconds, at which the corresponding handler should be
        #: called. Has the same zero as Timer.getFPGATime().
        self._expirationTime = 0

        #: The handler passed in by the user which should be called at the
        #: appropriate interval.
        self._handler = run

        # Whether we are calling the handler just once or periodically.
        self._periodic = False

        #: If periodic, the period of the calling; if just once, stores how long it
        #: is until we call the handler.
        self._period = 0

        #: The thread waiting on the HAL alarm
        self._thread = threading.Thread(target=self._run, name="Notifier", daemon=True)
        self._thread.start()

        # python-specific
        Resource._add_global_resource(self)

    def close(self) -> None:
        handle, self._notifier = self._notifier, None
        if not handle:
            return

        hal.stopNotifier(handle)

        # Join the thread to ensure the handler has exited.
        if self._thread.is_alive():
            # python-specific: interrupt not supported
            self._thread.join()

        hal.cleanNotifier(handle)
        self._thread = None

    def _updateAlarm(self, triggerTime=None) -> None:
        """
        Update the alarm hardware to reflect the next alarm.

        :param triggerTime: the time at which the next alarm will be triggered
        """
        if triggerTime is None:
            triggerTime = int(self._expirationTime * 1e6)
        handle = self._notifier
        if handle:
            hal.updateNotifierAlarm(handle, triggerTime)

    def _run(self) -> None:
        while True:
            notifier = self._notifier
            if not notifier:
                break

            curTime = hal.waitForNotifierAlarm(notifier)
            if curTime == 0:
                break

            with self._processLock:
                handler = self._handler
                if self._periodic:
                    self._expirationTime += self._period
                    self._updateAlarm()
                else:
                    # need to update the alarm to cause it to wait again
                    self._updateAlarm(-1)

            if handler:
                handler()

    def setHandler(self, handler: callable) -> None:
        """Change the handler function.
        
        :param handler: Handler
        """
        with self._processLock:
            self._handler = handler

    def startSingle(self, delay: float) -> None:
        """Register for single event notification.

        A timer event is queued for a single event after the specified delay.

        :param delay: Seconds to wait before the handler is called.
        """
        with self._processLock:
            self._periodic = False
            self._period = delay
            self._expirationTime = RobotController.getFPGATime() * 1e-6 + delay
            self._updateAlarm()

    def startPeriodic(self, period: float) -> None:
        """Register for periodic event notification.

        A timer event is queued for periodic event notification.
        Each time the interrupt occurs, the event will be immediately
        requeued for the same time interval.

        :param period: Period in seconds to call the handler starting
                       one period after the call to this method.
        """
        with self._processLock:
            self._periodic = True
            self._period = period
            self._expirationTime = RobotController.getFPGATime() * 1e-6 + period
            self._updateAlarm()

    def stop(self) -> None:
        """Stop timer events from occurring.

        Stop any repeating timer events from occurring. This will also
        remove any single notification events from the queue.
        If a timer-based call to the registered handler is in progress,
        this function will block until the handler call is complete.
        """
        hal.cancelNotifierAlarm(self._notifier)
