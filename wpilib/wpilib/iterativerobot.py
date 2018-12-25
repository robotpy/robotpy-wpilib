# validated: 2018-11-18 EN 81498e6af915 edu/wpi/first/wpilibj/IterativeRobot.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import warnings
import hal
import logging

from .iterativerobotbase import IterativeRobotBase

__all__ = ["IterativeRobot"]


class IterativeRobot(IterativeRobotBase):
    """IterativeRobot implements the IterativeRobotBase robot program framework.

    The IterativeRobot class is intended to be subclassed by a user creating a robot program.

    periodic() functions from the base class are called each time a new packet is received from
    the driver station.

    .. deprecated:: 2019.0.0
        Use TimedRobot instead. It's a drop-in replacement that provides more
        regular execution periods.
    """

    kPacketPeriod = 0.02

    #: A python logging object that you can use to send messages to the log. It
    #: is recommended to use this instead of print statements.
    logger = logging.getLogger("robot")

    def __init__(self) -> None:
        """Constructor for IterativeRobot.

        The constructor initializes the instance variables for the robot to
        indicate the status of initialization for disabled, autonomous, and
        teleop code.

        .. warning:: If you override ``__init__`` in your robot class, you must call
                     the base class constructor. This must be used to ensure that
                     the communications code starts.
        """
        super().__init__(IterativeRobot.kPacketPeriod)
        hal.report(
            hal.UsageReporting.kResourceType_Framework,
            hal.UsageReporting.kFramework_Iterative,
        )

    def __init_subclass__(cls, **kwargs) -> None:
        warnings.warn(
            "IterativeRobot is deprecated, use TimedRobot instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        super().__init_subclass__(**kwargs)

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()."""

        self.robotInit()

        # Tell the DS that the robot is ready to be enabled
        hal.observeUserProgramStarting()

        # loop forever, calling the appropriate mode-dependent function
        while True:
            # Wait for new data to arrive
            self.ds.waitForData()
            # Call the appropriate function depending upon the current robot mode
            self.loopFunc()
