# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.

import hal
import warnings

import logging
logger = logging.getLogger('robotpy')

__all__ = ["RobotBase"]

class RobotBase:
    """Implement a Robot Program framework.
    
    The RobotBase class is intended to be subclassed by a user creating a
    robot program.  Overridden autonomous() and operatorControl() methods
    are called at the appropriate time as the match proceeds. In the current
    implementation, the Autonomous code will run to completion before the
    OperatorControl code could start. In the future the Autonomous code might
    be spawned as a task, then killed at the end of the Autonomous period.
    
    User code should be placed in the constructor that runs before the
    Autonomous or Operator Control period starts. The constructor will
    run to completion before Autonomous is entered.

    .. warning:: If you override __init__ in your robot class, you must call
                 the base class constructor. This must be used to ensure that
                 the communications code starts.
    """

    def __init__(self):
        # TODO: StartCAPI()
        # TODO: See if the next line is necessary
        # Resource.RestartProgram()

        try:
            from networktables import NetworkTable
            #NetworkTable.setServerMode() -- don't set this explicitly, it's the default.
        except ImportError:
            warnings.warn("networktables not found", ImportWarning)
            NetworkTable = None

        from .driverstation import DriverStation
        self.ds = DriverStation.getInstance()

        if NetworkTable is not None:
            NetworkTable.getTable("")   # forces network tables to initialize
            NetworkTable.getTable("LiveWindow").getSubTable("~STATUS~").putBoolean("LW Enabled", False)

        self.__initialized = True

    def prestart(self):
        """
        This hook is called right before :meth:`startCompetition`. By default, tell
        the DS that the robot is now ready to be enabled. If you don't want the
        robot to be enabled yet, you can override this method to do nothing.
        If you do so, you will need to call hal.HALNetworkCommunicationObserveUserProgramStarting()
        from your code when you are ready for the robot to be enabled.
        """
        hal.HALNetworkCommunicationObserveUserProgramStarting()


    def free(self):
        """Free the resources for a RobotBase class."""
        # TODO: delete?
        pass

    @staticmethod
    def isSimulation():
        """
            :returns: If the robot is running in simulation.
            :rtype: bool
        """
        return hal.HALIsSimulation()

    @staticmethod
    def isReal():
        """
            :returns: If the robot is running in the real world.
            :rtype: bool
        """
        return not hal.HALIsSimulation()

    def isDisabled(self):
        """Determine if the Robot is currently disabled.

        :returns: True if the Robot is currently disabled by the field
            controls.
        :rtype: bool
        """
        return self.ds.isDisabled()

    def isEnabled(self):
        """Determine if the Robot is currently enabled.

        :returns: True if the Robot is currently enabled by the field
            controls.
        :rtype: bool
        """
        return self.ds.isEnabled()

    def isAutonomous(self):
        """Determine if the robot is currently in Autonomous mode.

        :returns: True if the robot is currently operating Autonomously as
            determined by the field controls.
        :rtype: bool
        """
        return self.ds.isAutonomous()

    def isTest(self):
        """Determine if the robot is currently in Test mode.

        :returns: True if the robot is currently operating in Test mode as
            determined by the driver station.
        :rtype: bool
        """
        return self.ds.isTest()

    def isOperatorControl(self):
        """Determine if the robot is currently in Operator Control mode.

        :returns: True if the robot is currently operating in Tele-Op mode as
            determined by the field controls.
        :rtype: bool
        """
        return self.ds.isOperatorControl()

    def isNewDataAvailable(self):
        """Indicates if new data is available from the driver station.

        :returns: Has new data arrived over the network since the last time
            this function was called?
        :rtype: bool
        """
        return self.ds.isNewControlData()

    def startCompetition(self):
        """Provide an alternate "main loop" via startCompetition()."""
        raise NotImplementedError

    @staticmethod
    def initializeHardwareConfiguration():
        """Common initialization for all robot programs."""
        hal.HALInitialize()

        from .driverstation import DriverStation
        from .robotstate import RobotState
        RobotState.impl = DriverStation.getInstance()

    @staticmethod
    def main(robot_cls):
        """Starting point for the applications."""
        RobotBase.initializeHardwareConfiguration()

        hal.HALReport(hal.HALUsageReporting.kResourceType_Language,
                      hal.HALUsageReporting.kLanguage_Python)

        try:
            robot = robot_cls()
            robot.prestart()
        except:
            from .driverstation import DriverStation
            DriverStation.reportError("ERROR Could not instantiate robot", True)
            logger.exception("Robots don't quit!")
            logger.exception("Could not instantiate robot "+robot_cls.__name__+"!")
            return False
        
        # Add a check to see if the user forgot to call super().__init__()
        if not hasattr(robot, '_RobotBase__initialized'):
            logger.error("If your robot class has an __init__ function, it must call super().__init__()!")
            return False
        
        if not hal.HALIsSimulation():
            try:
                import wpilib
                with open('/tmp/frc_versions/FRC_Lib_Version.ini', 'w') as fp:
                    fp.write('RobotPy %s' % wpilib.__version__)
            except:
                logger.warning("Could not write FRC version file to disk")

        try:
            robot.startCompetition()
        except KeyboardInterrupt:
            logger.exception("THIS IS NOT AN ERROR: The user hit CTRL-C to kill the robot")
            logger.info("Exiting because of keyboard interrupt")
            return True
        except:
            from .driverstation import DriverStation
            DriverStation.reportError("ERROR Unhandled exception", True)
            logger.warn("Robots don't quit!")
            logger.exception("---> The startCompetition() method (or methods called by it) should have handled the exception.")
            return False
        else:
            # startCompetition never returns unless exception occurs....
            from .driverstation import DriverStation
            DriverStation.reportError("ERROR startCompetition() returned", False)
            logger.warn("Robots don't quit!")
            logger.error("---> Unexpected return from startCompetition() method.")
            return False