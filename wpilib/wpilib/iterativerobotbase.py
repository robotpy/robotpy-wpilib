# validated: 2019-02-16 DS 7d195963676c edu/wpi/first/wpilibj/IterativeRobotBase.java
# ----------------------------------------------------------------------------
# Copyright (c) 2017-2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum
import logging

import hal
from .livewindow import LiveWindow
from .smartdashboard import SmartDashboard
from .driverstation import DriverStation
from .robotbase import RobotBase
from .watchdog import Watchdog
from .shuffleboard import Shuffleboard

__all__ = ["IterativeRobotBase"]


class IterativeRobotBase(RobotBase):
    """IterativeRobotBase implements a specific type of robot program framework, extending the RobotBase
    class.

    The IterativeRobotBase class does not implement startCompetition(), so it should not be used
    by teams directly.

    This class provides the following functions which are called by the main loop,
    startCompetition(), at the appropriate times:

    robotInit() -- provide for initialization at robot power-on

    init() functions -- each of the following functions is called once when the
    appropriate mode is entered:

    - disabledInit()   -- called each and every time disabled is entered from
      another mode
    - autonomousInit() -- called each and every time autonomous is entered from
      another mode
    - teleopInit()     -- called each and every time teleop is entered from
      another mode
    - testInit()       -- called each and every time test is entered from
      another mode

    periodic() functions -- each of these functions is called on an interval:

    - robotPeriodic()
    - disabledPeriodic()
    - autonomousPeriodic()
    - teleopPeriodic()
    - testPeriodic()
    """

    class Mode(enum.IntEnum):
        kNone = 0
        kDisabled = 1
        kAutonomous = 2
        kTeleop = 3
        kTest = 4

    #: A python logging object that you can use to send messages to the log. It
    #: is recommended to use this instead of print statements.
    logger = logging.getLogger("robot")

    # ----------- Overridable initialization code -----------------

    def __init__(self, period: float) -> None:
        """Constructor for IterativeRobotBase.

        :param period: Period in seconds
        """
        super().__init__()
        self.last_mode = self.Mode.kNone
        self.period = period
        self.watchdog = Watchdog(period, self.printLoopOverrunMessage)

    def robotInit(self) -> None:
        """Robot-wide initialization code should go here.

        Users should override this method for default Robot-wide initialization
        which will be called when the robot is first powered on.  It will be
        called exactly 1 time.

        .. note:: It is simpler to override this function instead of defining
                  a constructor for your robot class
        """
        self.logger.info("Default IterativeRobot.robotInit() method... Override me!")

    def disabledInit(self) -> None:
        """Initialization code for disabled mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters disabled mode.
        """
        self.logger.info("Default IterativeRobot.disabledInit() method... Override me!")

    def autonomousInit(self) -> None:
        """Initialization code for autonomous mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters autonomous mode.
        """
        self.logger.info(
            "Default IterativeRobot.autonomousInit() method... Override me!"
        )

    def teleopInit(self) -> None:
        """Initialization code for teleop mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters teleop mode.
        """
        self.logger.info("Default IterativeRobot.teleopInit() method... Override me!")

    def testInit(self) -> None:
        """Initialization code for test mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters test mode.
        """
        self.logger.info("Default IterativeRobot.testInit() method... Override me!")

    # ----------- Overridable periodic code -----------------

    def robotPeriodic(self) -> None:
        """Periodic code for all robot modes should go here."""
        func = self.robotPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info(
                "Default IterativeRobot.robotPeriodic() method... Override me!"
            )
            func.firstRun = False

    def disabledPeriodic(self) -> None:
        """Periodic code for disabled mode should go here."""
        func = self.disabledPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info(
                "Default IterativeRobot.disabledPeriodic() method... Override me!"
            )
            func.firstRun = False

    def autonomousPeriodic(self) -> None:
        """Periodic code for autonomous mode should go here."""
        func = self.autonomousPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info(
                "Default IterativeRobot.autonomousPeriodic() method... Override me!"
            )
            func.firstRun = False

    def teleopPeriodic(self) -> None:
        """Periodic code for teleop mode should go here."""
        func = self.teleopPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.warning(
                "Default IterativeRobot.teleopPeriodic() method... Override me!"
            )
            func.firstRun = False

    def testPeriodic(self) -> None:
        """Periodic code for test mode should go here."""
        func = self.testPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info(
                "Default IterativeRobot.testPeriodic() method... Override me!"
            )
            func.firstRun = False

    def loopFunc(self) -> None:
        """Call the appropriate function depending upon the current robot mode"""
        self.watchdog.reset()

        isEnabled, isAutonomous, isTest = self.getControlState()

        if not isEnabled:
            if self.last_mode is not self.Mode.kDisabled:
                LiveWindow.setEnabled(False)
                Shuffleboard.disableActuatorWidgets()
                self.disabledInit()
                self.watchdog.addEpoch("disabledInit()")
                self.last_mode = self.Mode.kDisabled
            hal.observeUserProgramDisabled()
            self.disabledPeriodic()
            self.watchdog.addEpoch("disabledPeriodic()")
        elif isAutonomous:
            if self.last_mode is not self.Mode.kAutonomous:
                LiveWindow.setEnabled(False)
                Shuffleboard.disableActuatorWidgets()
                self.autonomousInit()
                self.watchdog.addEpoch("autonomousInit()")
                self.last_mode = self.Mode.kAutonomous
            hal.observeUserProgramAutonomous()
            self.autonomousPeriodic()
            self.watchdog.addEpoch("autonomousPeriodic()")
        elif not isTest:
            if self.last_mode is not self.Mode.kTeleop:
                LiveWindow.setEnabled(False)
                Shuffleboard.disableActuatorWidgets()
                self.teleopInit()
                self.watchdog.addEpoch("teleopInit()")
                self.last_mode = self.Mode.kTeleop
            hal.observeUserProgramTeleop()
            self.teleopPeriodic()
            self.watchdog.addEpoch("teleopPeriodic()")
        else:
            if self.last_mode is not self.Mode.kTest:
                LiveWindow.setEnabled(True)
                Shuffleboard.enableActuatorWidgets()
                self.testInit()
                self.watchdog.addEpoch("testInit()")
                self.last_mode = self.Mode.kTest
            hal.observeUserProgramTest()
            self.testPeriodic()
            self.watchdog.addEpoch("testPeriodic()")
        self.robotPeriodic()
        self.watchdog.addEpoch("robotPeriodic()")
        self.watchdog.disable()
        SmartDashboard.updateValues()
        LiveWindow.updateValues()
        Shuffleboard.update()

        if self.watchdog.isExpired():
            self.watchdog.printEpochs()

    def printLoopOverrunMessage(self) -> None:
        DriverStation.reportWarning(
            "Loop time of %ss overrun\n" % (self.period,), False
        )
