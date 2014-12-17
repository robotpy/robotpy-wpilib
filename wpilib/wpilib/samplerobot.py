#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import logging

from .robotbase import RobotBase
from .timer import Timer
from .livewindow import LiveWindow

__all__ = ["SampleRobot"]

class SampleRobot(RobotBase):
    """A simple robot base class that knows the standard FRC competition
    states (disabled, autonomous, or operator controlled).

    You can build a simple robot program off of this by overriding the
    :meth:`robotinit`, :meth:`disabled`, :meth:`autonomous` and
    :meth:`operatorControl` methods. The :meth:`startCompetition` method
    will call these methods (sometimes repeatedly) depending on the state
    of the competition.

    Alternatively you can override the :meth:`robotMain` method and manage all
    aspects of the robot yourself (not recommended).
    
    .. warning:: While it may look like a good choice to use for your code
                 if you're inexperienced, don't. Unless you know what you
                 are doing, complex code will be much more difficult under
                 this system. Use :class:`.IterativeRobot` or command based
                 instead if you're new.
    """
    
    #: A python logging object that you can use to send messages to the log. It
    #: is recommended to use this instead of print statements.
    logger = logging.getLogger("robot")

    def robotInit(self):
        """Robot-wide initialization code should go here.

        Users should override this method for default Robot-wide initialization
        which will be called when the robot is first powered on.  It will be
        called exactly 1 time.
        
        .. note:: It is simpler to override this function instead of defining
                  a constructor for your robot class
        """
        self.logger.info("Default robotInit() method running, consider providing your own")

    def disabled(self):
        """Disabled should go here.
        Users should overload this method to run code that should run while
        the field is disabled.

        Called once each time the robot enters the disabled state.
        """
        self.logger.info("Default disabled() method running, consider providing your own")

    def autonomous(self):
        """Autonomous should go here.
        Users should add autonomous code to this method that should run while
        the field is in the autonomous period.

        Called once each time the robot enters the autonomous state.
        """
        self.logger.info("Default autonomous() method running, consider providing your own")

    def operatorControl(self):
        """Operator control (tele-operated) code should go here.
        Users should add Operator Control code to this method that should run
        while the field is in the Operator Control (tele-operated) period.

        Called once each time the robot enters the operator-controlled state.
        """
        self.logger.warn("Default operatorControl() method running, consider providing your own")

    def test(self):
        """Test code should go here.
        Users should add test code to this method that should run while the
        robot is in test mode.
        """
        self.logger.info("Default test() method running, consider providing your own")

    def robotMain(self):
        """Robot main program for free-form programs.

        This should be overridden by user subclasses if the intent is to not
        use the autonomous() and operatorControl() methods. In that case, the
        program is responsible for sensing when to run the autonomous and
        operator control functions in their program.

        This method will be called immediately after the constructor is
        called. If it has not been overridden by a user subclass (i.e. the
        default version runs), then the robotInit(), disabled(), autonomous()
        and operatorControl() methods will be called.
        """
        self._no_robot_main = True

    def startCompetition(self):
        """Start a competition.
        This code tracks the order of the field starting to ensure that
        everything happens in the right order. Repeatedly run the correct
        method, either Autonomous or OperatorControl when the robot is
        enabled. After running the correct method, wait for some state to
        change, either the other mode starts or the robot is disabled. Then
        go back and wait for the robot to be enabled again.
        """
        hal.HALReport(hal.HALUsageReporting.kResourceType_Framework,
                      hal.HALUsageReporting.kFramework_Simple)

        self.robotMain()
            
        if hasattr(self, '_no_robot_main'):
            # first and one-time initialization
            LiveWindow.setEnabled(False)
            self.robotInit()

            while True:
                if self.isDisabled():
                    self.ds.InDisabled(True)
                    self.disabled()
                    self.ds.InDisabled(False)
                    while self.isDisabled():
                        Timer.delay(0.01)
                elif self.isAutonomous():
                    self.ds.InAutonomous(True)
                    self.autonomous()
                    self.ds.InAutonomous(False)
                    while self.isAutonomous() and not self.isDisabled():
                        Timer.delay(0.01)
                elif self.isTest():
                    LiveWindow.setEnabled(True)
                    self.ds.InTest(True)
                    self.test()
                    self.ds.InTest(False)
                    while self.isTest() and self.isEnabled():
                        Timer.delay(0.01)
                    LiveWindow.setEnabled(False)
                else:
                    self.ds.InOperatorControl(True)
                    self.operatorControl()
                    self.ds.InOperatorControl(False)
                    while self.isOperatorControl() and not self.isDisabled():
                        Timer.delay(0.01)
