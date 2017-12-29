# validated: 2017-11-09 TW ef3267833fc3 edu/wpi/first/wpilibj/TimedRobot.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .iterativerobotbase import IterativeRobotBase
from .notifier import Notifier
from .timer import Timer


__all__ = ["TimedRobot"]


class TimedRobot(IterativeRobotBase):
    """TimedRobot implements the IterativeRobotBase robot program framework.

    The TimedRobot class is intended to be subclassed by a user creating a robot program.

    periodic() functions from the base class are called on an interval by a Notifier instance.
    """
    DEFAULT_PERIOD = .02


    def __init__(self):
        super().__init__()
        hal.report(hal.UsageReporting.kResourceType_Framework, hal.UsageReporting.kFramework_Iterative)

        self.period = TimedRobot.DEFAULT_PERIOD
        # Prevents loop from starting if user calls setPeriod() in robotInit()
        self.startLoop = False
        self.loop = Notifier(self.loopFunc)

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()"""
        self.robotInit()

        hal.observeUserProgramStarting()

        self.startLoop = True
        self.loop.startPeriodic(self.period)

        while True:
            Timer.delay(60*60*24)


    def setPeriod(self, period: float) -> None:
        """Set time period between calls to Periodic() functions.

        :param period: Period in seconds
        """
        self.period = period

        if self.startLoop:
            self.loop.startPeriodic(self.period)
