# validated: 2017-12-06 DV dd7563376bf6 edu/wpi/first/wpilibj/RobotBase.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
from networktables import NetworkTables

import logging
logger = logging.getLogger('robotpy')

__all__ = ["RobotBase"]

class RobotBase:
    """Implement a Robot Program framework.

    The RobotBase class is intended to be subclassed by a user creating a
    robot program.  Overridden ``autonomous()`` and ``operatorControl()`` methods
    are called at the appropriate time as the match proceeds. In the current
    implementation, the Autonomous code will run to completion before the
    OperatorControl code could start. In the future the Autonomous code might
    be spawned as a task, then killed at the end of the Autonomous period.

    User code should be placed in the constructor that runs before the
    Autonomous or Operator Control period starts. The constructor will
    run to completion before Autonomous is entered.

    .. warning:: If you override ``__init__`` in your robot class, you must call
                 the base class constructor. This must be used to ensure that
                 the communications code starts.

    .. not_implemented: getBooleanProperty
    """

    def __init__(self):
        NetworkTables.setNetworkIdentity("Robot")

        if self.isReal():
            NetworkTables.startServer("/home/lvuser/networktables.ini")
        else:
            NetworkTables.startServer()

        from .driverstation import DriverStation
        self.ds = DriverStation.getInstance()

        NetworkTables.getTable("LiveWindow").getSubTable(".status").getEntry("LW Enabled").setBoolean(False)
        from .livewindow import LiveWindow
        LiveWindow.setEnabled(False)

        self.__initialized = True

    def free(self):
        """Free the resources for a RobotBase class."""
        pass

    @staticmethod
    def isSimulation() -> bool:
        """Get if the robot is a simulation.

        :returns: If the robot is running in simulation.
        """
        return hal.isSimulation()

    @staticmethod
    def isReal() -> bool:
        """Get if the robot is real.

        :returns: If the robot is running in the real world.
        """
        return not hal.isSimulation()

    def isDisabled(self) -> bool:
        """Determine if the Robot is currently disabled.

        :returns: True if the Robot is currently disabled by the field controls.
        """
        return self.ds.isDisabled()

    def isEnabled(self) -> bool:
        """Determine if the Robot is currently enabled.

        :returns: True if the Robot is currently enabled by the field controls.
        """
        return self.ds.isEnabled()

    def isAutonomous(self) -> bool:
        """Determine if the robot is currently in Autonomous mode as
        determined by the field controls.

        :returns: True if the robot is currently operating Autonomously
        """
        return self.ds.isAutonomous()

    def isTest(self) -> bool:
        """Determine if the robot is currently in Test mode as
        determined by the driver station.

        :returns: True if the robot is currently operating in Test mode.
        """
        return self.ds.isTest()

    def isOperatorControl(self) -> bool:
        """Determine if the robot is currently in Operator Control mode as
        determined by the field controls.

        :returns: True if the robot is currently operating in Tele-Op mode
        """
        return self.ds.isOperatorControl()

    def isNewDataAvailable(self) -> bool:
        """Indicates if new data is available from the driver station.

        :returns: Has new data arrived over the network since the last time
                  this function was called?
        """
        return self.ds.isNewControlData()

    def startCompetition(self):
        """Provide an alternate "main loop" via startCompetition()."""
        raise NotImplementedError

    @staticmethod
    def initializeHardwareConfiguration():
        """Common initialization for all robot programs."""

        # Python specific: do not call this, initialize() is already called when
        # hal is imported
        #hal.initialize()

        from .driverstation import DriverStation
        from .robotstate import RobotState
        RobotState.impl = DriverStation.getInstance()

    @staticmethod
    def main(robot_cls):
        """Starting point for the applications."""
        RobotBase.initializeHardwareConfiguration()

        hal.report(hal.UsageReporting.kResourceType_Language,
                   hal.UsageReporting.kLanguage_Python)

        try:
            robot = robot_cls()
        except:
            from .driverstation import DriverStation
            DriverStation.reportError("Unhandled exception instantiating robot " + robot_cls.__name__, True)
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError("Could not instantiate robot "+robot_cls.__name__+"!", False)
            return False

        # Add a check to see if the user forgot to call super().__init__()
        if not hasattr(robot, '_RobotBase__initialized'):
            logger.error("If your robot class has an __init__ function, it must call super().__init__()!")
            return False

        if not hal.isSimulation():
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
            DriverStation.reportError("Unhandled exception", True)
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError("The startCompetition() method (or methods called by it) should have handled the exception above.", False)
            return False
        else:
            # startCompetition never returns unless exception occurs....
            from .driverstation import DriverStation
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError("Unexpected return from startCompetition() method.", False)
            return False
