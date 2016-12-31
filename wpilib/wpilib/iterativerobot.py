# validated: 2016-12-22 JW e65f9908d774 athena/java/edu/wpi/first/wpilibj/IterativeRobot.java
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

__all__ = ["IterativeRobot"]

class IterativeRobot(RobotBase):
    """IterativeRobot implements a specific type of Robot Program framework,
    extending the :class:`.RobotBase` class.

    The IterativeRobot class is intended to be subclassed by a user creating a
    robot program.

    This class is intended to implement the "old style" default code, by
    providing the following functions which are called by the main loop,
    :meth:`startCompetition`, at the appropriate times:

    - :meth:`robotInit` -- provide for initialization at robot power-on

    init() functions -- each of the following functions is called once when the
    appropriate mode is entered:

    - :meth:`disabledInit`   -- called only when first disabled
    - :meth:`autonomousInit` -- called each and every time autonomous is entered from another mode
    - :meth:`teleopInit`     -- called each and every time teleop is entered from another mode
    - :meth:`testInit`       -- called each and every time test mode is entered from another mode

    Periodic() functions -- each of these functions is called iteratively at
    the appropriate periodic rate (aka the "slow loop").  The period of
    the iterative robot is synced to the driver station control packets,
    giving a periodic frequency of about 50Hz (50 times per second).
    
    - :meth:`disabledPeriodic`
    - :meth:`autonomousPeriodic`
    - :meth:`teleopPeriodic`
    - :meth:`testPeriodic`
    
    """
     
    #: A python logging object that you can use to send messages to the log. It
    #: is recommended to use this instead of print statements.
    logger = logging.getLogger("robot")

    def __init__(self):
        """Constructor for RobotIterativeBase.

        The constructor initializes the instance variables for the robot to
        indicate the status of initialization for disabled, autonomous, and
        teleop code.
        
        .. warning:: If you override ``__init__`` in your robot class, you must call
                     the base class constructor. This must be used to ensure that
                     the communications code starts.
        """
        super().__init__()
        # set status for initialization of disabled, autonomous, and teleop code.
        self.disabledInitialized = False
        self.autonomousInitialized = False
        self.teleopInitialized = False
        self.testInitialized = False

    def startCompetition(self):
        """Provide an alternate "main loop" via startCompetition()."""
        hal.report(hal.UsageReporting.kResourceType_Framework,
                      hal.UsageReporting.kFramework_Iterative)

        self.robotInit()

        # Tell the DS that the robot is ready to be enabled
        hal.observeUserProgramStarting()

        # loop forever, calling the appropriate mode-dependent function
        LiveWindow.setEnabled(False)
        while True:
            # Wait for new data to arrive
            self.ds.waitForData()
            # Call the appropriate function depending upon the current robot mode
            if self.isDisabled():
                # call DisabledInit() if we are now just entering disabled mode from
                # either a different mode or from power-on
                if not self.disabledInitialized:
                    LiveWindow.setEnabled(False)
                    self.disabledInit()
                    self.disabledInitialized = True
                    # reset the initialization flags for the other modes
                    self.autonomousInitialized = False
                    self.teleopInitialized = False
                    self.testInitialized = False
                hal.observeUserProgramDisabled()
                self.disabledPeriodic()
            elif self.isTest():
                # call TestInit() if we are now just entering test mode from either
                # a different mode or from power-on
                if not self.testInitialized:
                    LiveWindow.setEnabled(True)
                    self.testInit()
                    self.testInitialized = True
                    self.autonomousInitialized = False
                    self.teleopInitialized = False
                    self.disabledInitialized = False
                hal.observeUserProgramTest()
                self.testPeriodic()
            elif self.isAutonomous():
                # call Autonomous_Init() if this is the first time
                # we've entered autonomous_mode
                if not self.autonomousInitialized:
                    LiveWindow.setEnabled(False)
                    # KBS NOTE: old code reset all PWMs and relays to "safe values"
                    # whenever entering autonomous mode, before calling
                    # "Autonomous_Init()"
                    self.autonomousInit()
                    self.autonomousInitialized = True
                    self.testInitialized = False
                    self.teleopInitialized = False
                    self.disabledInitialized = False
                hal.observeUserProgramAutonomous()
                self.autonomousPeriodic()
            else:
                # call Teleop_Init() if this is the first time
                # we've entered teleop_mode
                if not self.teleopInitialized:
                    LiveWindow.setEnabled(False)
                    self.teleopInit()
                    self.teleopInitialized = True
                    self.testInitialized = False
                    self.autonomousInitialized = False
                    self.disabledInitialized = False
                hal.observeUserProgramTeleop()
                self.teleopPeriodic()
            self.robotPeriodic()

    # ----------- Overridable initialization code -----------------

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
        """Periodic code for all robot modes should go here.

        This function is called each time a new packet is received from the driver station.

        Packets are received approximately every 20ms.  Fixed loop timing is not guaranteed due to
        network timing variability and the function may not be called at all if the Driver Station is
        disconnected.  For most use cases the variable timing will not be an issue.  If your code does
        require guaranteed fixed periodic timing, consider using Notifier or PIDController instead.
        """
        func = self.robotPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.robotPeriodic() method... Overload me!")
            func.firstRun = False

    def disabledPeriodic(self):
        """Periodic code for disabled mode should go here.

        Users should override this method for code which will be called each time a new packet is
        received from the driver station and the robot is in disabled mode.

        Packets are received approximately every 20ms.  Fixed loop timing is not guaranteed due to
        network timing variability and the function may not be called at all if the Driver Station is
        disconnected.  For most use cases the variable timing will not be an issue.  If your code does
        require guaranteed fixed periodic timing, consider using Notifier or PIDController instead.
        """
        func = self.disabledPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.disabledPeriodic() method... Overload me!")
            func.firstRun = False

    def autonomousPeriodic(self):
        """Periodic code for autonomous mode should go here.

        Users should override this method for code which will be called each time a new packet is
        received from the driver station and the robot is in autonomous mode.

        Packets are received approximately every 20ms.  Fixed loop timing is not guaranteed due to
        network timing variability and the function may not be called at all if the Driver Station is
        disconnected.  For most use cases the variable timing will not be an issue.  If your code does
        require guaranteed fixed periodic timing, consider using Notifier or PIDController instead.
        """
        func = self.autonomousPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.autonomousPeriodic() method... Overload me!")
            func.firstRun = False

    def teleopPeriodic(self):
        """Periodic code for teleop mode should go here.

        Users should override this method for code which will be called each time a new packet is
        received from the driver station and the robot is in teleop mode.

        Packets are received approximately every 20ms.  Fixed loop timing is not guaranteed due to
        network timing variability and the function may not be called at all if the Driver Station is
        disconnected.  For most use cases the variable timing will not be an issue.  If your code does
        require guaranteed fixed periodic timing, consider using Notifier or PIDController instead.
        """
        func = self.teleopPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.warn("Default IterativeRobot.teleopPeriodic() method... Overload me!")
            func.firstRun = False

    def testPeriodic(self):
        """Periodic code for test mode should go here.

        Users should override this method for code which will be called each time a new packet is
        received from the driver station and the robot is in test mode.

        Packets are received approximately every 20ms.  Fixed loop timing is not guaranteed due to
        network timing variability and the function may not be called at all if the Driver Station is
        disconnected.  For most use cases the variable timing will not be an issue.  If your code does
        require guaranteed fixed periodic timing, consider using Notifier or PIDController instead.
        """
        func = self.testPeriodic.__func__
        if not hasattr(func, "firstRun"):
            self.logger.info("Default IterativeRobot.testPeriodic() method... Overload me!")
            func.firstRun = False
