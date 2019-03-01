# validated: 2018-12-31 TW d817001259d6 edu/wpi/first/wpilibj/RobotBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2018. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Tuple, Type

import hal
from networktables import NetworkTables

import logging

logger = logging.getLogger("robotpy")

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

    def __init__(self) -> None:
        NetworkTables.setNetworkIdentity("Robot")

        if self.isReal():
            NetworkTables.startServer("/home/lvuser/networktables.ini")
        else:
            NetworkTables.startServer()

        from .driverstation import DriverStation

        self.ds = DriverStation.getInstance()

        # python-specific micro-optimization: attach all of the ds methods
        # to this object to avoid an extra function call
        self.getControlState = self.ds.getControlState
        self.isDisabled = self.ds.isDisabled
        self.isEnabled = self.ds.isEnabled
        self.isAutonomous = self.ds.isAutonomous
        self.isAutonomousEnabled = self.ds.isAutonomousEnabled
        self.isTest = self.ds.isTest
        self.isOperatorControl = self.ds.isOperatorControl
        self.isOperatorControlEnabled = self.ds.isOperatorControlEnabled
        self.isNewDataAvailable = self.ds.isNewControlData

        NetworkTables.getTable("LiveWindow").getSubTable(".status").getEntry(
            "LW Enabled"
        ).setBoolean(False)
        from .livewindow import LiveWindow

        LiveWindow.setEnabled(False)

        from .shuffleboard.shuffleboard import Shuffleboard

        Shuffleboard.disableActuatorWidgets()

        self.__initialized = True

    def free(self) -> None:
        """Free the resources for a RobotBase class.

        .. deprecated:: 2019.0.0
            Use :meth:`close` instead"""
        pass

    def close(self) -> None:
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

    def getControlState(self) -> Tuple[bool, bool, bool]:
        """More efficient way to determine what state the robot is in.

        :returns: booleans representing enabled, isautonomous, istest

        .. versionadded:: 2019.2.1

        .. note:: This function only exists in RobotPy
        """
        return self.ds.getControlState()

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

    def isAutonomousEnabled(self) -> bool:
        """Equivalent to calling ``isAutonomous() and isEnabled()`` but
        more efficient.

        :returns: True if the robot is in autonomous mode and is enabled,
            False otherwise.
        
        .. versionadded:: 2019.2.1

        .. note:: This function only exists in RobotPy
        """
        return self.ds.isAutonomousEnabled()

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

    def isOperatorControlEnabled(self) -> bool:
        """Equivalent to calling ``isOperatorControl() and isEnabled()`` but
        more efficient.

        :returns: True if the robot is in operator-controlled mode and is enabled,
            False otherwise.
        
        .. versionadded:: 2019.2.1

        .. note:: This function only exists in RobotPy
        """
        return self.ds.isOperatorControlEnabled()

    def isNewDataAvailable(self) -> bool:
        """Indicates if new data is available from the driver station.

        :returns: Has new data arrived over the network since the last time
                  this function was called?
        """
        return self.ds.isNewControlData()

    def startCompetition(self) -> None:
        """Provide an alternate "main loop" via startCompetition()."""
        raise NotImplementedError

    @staticmethod
    def main(robot_cls: Type["RobotBase"]) -> bool:
        """Starting point for the applications."""
        # Python-specific: don't call hal.initialize() again here.
        hal.report(
            hal.UsageReporting.kResourceType_Language,
            hal.UsageReporting.kLanguage_Python,
        )

        try:
            robot = robot_cls()
        except:
            from .driverstation import DriverStation

            DriverStation.reportError(
                "Unhandled exception instantiating robot " + robot_cls.__name__, True
            )
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError(
                "Could not instantiate robot " + robot_cls.__name__ + "!", False
            )
            return False

        # Add a check to see if the user forgot to call super().__init__()
        if not hasattr(robot, "_RobotBase__initialized"):
            logger.error(
                "If your robot class has an __init__ function, it must call super().__init__()!"
            )
            return False

        if not hal.isSimulation():
            try:
                import wpilib

                with open("/tmp/frc_versions/FRC_Lib_Version.ini", "w") as fp:
                    fp.write("RobotPy %s" % wpilib.__version__)
            except:
                from .driverstation import DriverStation

                DriverStation.reportError(
                    "Could not write FRC version file to disk", True
                )

        try:
            robot.startCompetition()
        except KeyboardInterrupt:
            logger.exception(
                "THIS IS NOT AN ERROR: The user hit CTRL-C to kill the robot"
            )
            logger.info("Exiting because of keyboard interrupt")
            return True
        except:
            from .driverstation import DriverStation

            DriverStation.reportError("Unhandled exception", True)
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError(
                "The startCompetition() method (or methods called by it) should have handled the exception above.",
                False,
            )
            return False
        else:
            # startCompetition never returns unless exception occurs....
            from .driverstation import DriverStation

            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError(
                "Unexpected return from startCompetition() method.", False
            )
            return False
