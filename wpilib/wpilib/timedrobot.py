# validated: 2018-11-10 EN 0e9172f9a708 edu/wpi/first/wpilibj/TimedRobot.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Optional

import hal

from .iterativerobotbase import IterativeRobotBase
from .notifier import Notifier
from .resource import Resource
from .robotcontroller import RobotController
from .timer import Timer


__all__ = ["TimedRobot"]


class TimedRobot(IterativeRobotBase):
    """TimedRobot implements the IterativeRobotBase robot program framework.

    The TimedRobot class is intended to be subclassed by a user creating a robot program.

    periodic() functions from the base class are called on an interval by a Notifier instance.
    """

    kDefaultPeriod = 0.02

    def __init__(self, period: Optional[float] = None) -> None:
        if period is None:
            period = TimedRobot.kDefaultPeriod
        super().__init__(period)
        hal.report(
            hal.UsageReporting.kResourceType_Framework,
            hal.UsageReporting.kFramework_Timed,
        )

        self._expirationTime = 0
        self._notifier = hal.initializeNotifier()

        Resource._add_global_resource(self)

    # python-specific
    def free(self) -> None:
        hal.stopNotifier(self._notifier)
        hal.cleanNotifier(self._notifier)

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()"""
        self.robotInit()

        hal.observeUserProgramStarting()

        self._expirationTime = RobotController.getFPGATime() * 1e-6 + self.period
        self._updateAlarm()

        # Loop forever, calling the appropriate mode-dependent function
        while True:
            if hal.waitForNotifierAlarm(self._notifier) == 0:
                break

            self._expirationTime += self.period
            self._updateAlarm()

            self.loopFunc()

    def getPeriod(self) -> float:
        """Get time period between calls to Periodic() functions."""
        return self.period

    def _updateAlarm(self) -> None:
        """Update the alarm hardware to reflect the next alarm."""
        hal.updateNotifierAlarm(self._notifier, int(self._expirationTime * 1e6))
