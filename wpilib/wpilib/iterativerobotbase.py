# validated: 2018-01-01 EN 40eb6dfc9b83 edu/wpi/first/wpilibj/IterativeRobotBase.java
# ----------------------------------------------------------------------------
# Copyright (c) 2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import enum
import logging

import hal
from .livewindow import LiveWindow
from .smartdashboard import SmartDashboard
from .robotbase import RobotBase

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
    - disabledInit()   -- called only when first disabled
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

    class Mode(enum.Enum):
        kNone = 0
        kDisabled = 1
        kAutonomous = 2
        kTeleop = 3
        kTest = 4

    #: A python logging object that you can use to send messages to the log. It
    #: is recommended to use this instead of print statements.
    logger = logging.getLogger("robot")

    # ----------- Overridable initialization code -----------------

    def __init__(self):
        self.last_mode = self.Mode.kNone
        super().__init__()

    def robotInit(self):
        """Robot-wide initialization code should go here.

        Users should override this method for default Robot-wide initialization
        which will be called when the robot is first powered on.  It will be
        called exactly 1 time.

        .. note:: It is simpler to override this function instead of defining
                  a constructor for your robot class
        """
        self.logger.info("Default IterativeRobot.robotInit() method... Overload me!")

    def disabledInit(self):
        """Initialization code for disabled mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters disabled mode.
        """
        self.logger.info("Default IterativeRobot.disabledInit() method... Overload me!")

    def autonomousInit(self):
        """Initialization code for autonomous mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters autonomous mode.
        """
        self.logger.info("Default IterativeRobot.autonomousInit() method... Overload me!")

    def teleopInit(self):
        """Initialization code for teleop mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters teleop mode.
        """
        self.logger.info("Default IterativeRobot.teleopInit() method... Overload me!")

    def testInit(self):
        """Initialization code for test mode should go here.

        Users should override this method for initialization code which will be
        called each time the robot enters test mode.
        """
        self.logger.info("Default IterativeRobot.testInit() method... Overload me!")

    # ----------- Overridable periodic code -----------------

    def robotPeriodic(self):
        """Periodic code for all robot modes should go here."""
        func = self.robotPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.robotPeriodic() method... Overload me!")
            func.firstRun = False

    def disabledPeriodic(self):
        """Periodic code for disabled mode should go here."""
        func = self.disabledPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.disabledPeriodic() method... Overload me!")
            func.firstRun = False

    def autonomousPeriodic(self):
        """Periodic code for autonomous mode should go here."""
        func = self.autonomousPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.autonomousPeriodic() method... Overload me!")
            func.firstRun = False

    def teleopPeriodic(self):
        """Periodic code for teleop mode should go here."""
        func = self.teleopPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.warning("Default IterativeRobot.teleopPeriodic() method... Overload me!")
            func.firstRun = False

    def testPeriodic(self):
        """Periodic code for test mode should go here."""
        func = self.testPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.testPeriodic() method... Overload me!")
            func.firstRun = False

    def loopFunc(self):
        """Call the appropriate function depending upon the current robot mode"""

        if self.isDisabled():
            if self.last_mode is not self.Mode.kDisabled:
                LiveWindow.setEnabled(False)
                self.disabledInit()
                self.last_mode = self.Mode.kDisabled
            hal.observeUserProgramDisabled()
            self.disabledPeriodic()
        elif self.isAutonomous():
            if self.last_mode is not self.Mode.kAutonomous:
                LiveWindow.setEnabled(False)
                self.autonomousInit()
                self.last_mode = self.Mode.kAutonomous
            hal.observeUserProgramAutonomous()
            self.autonomousPeriodic()
        elif self.isOperatorControl():
            if self.last_mode is not self.Mode.kTeleop:
                LiveWindow.setEnabled(False)
                self.teleopInit()
                self.last_mode = self.Mode.kTeleop
            hal.observeUserProgramTeleop()
            self.teleopPeriodic()
        else:
            if self.last_mode is not self.Mode.kTest:
                LiveWindow.setEnabled(False)
                self.testInit()
                self.last_mode = self.Mode.kTest
            hal.observeUserProgramTest()
            self.testPeriodic()
        self.robotPeriodic()
        SmartDashboard.updateValues()
        LiveWindow.updateValues()
