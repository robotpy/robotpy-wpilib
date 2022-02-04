import hal
import wpilib
import logging
import threading

from wpilib import SmartDashboard
from .report_error import reportError, reportErrorInternal


class Main:
    """
    Executes the robot code using the currently installed HAL (this is probably not what you want unless you're on the roboRIO)
    """

    def __init__(self, parser):
        pass

    def run(self, options, robot_class, **static_options):
        return robot_class.main(robot_class)


class RobotStarter:
    def __init__(self):
        self.logger = logging.getLogger("robotpy")
        self.robot = None
        self.suppressExitWarning = False

    def run(self, robot_cls: wpilib.RobotBase) -> bool:
        if hal.hasMain():
            rval = [False]

            def _start():
                try:
                    rval[0] = self.start(robot_cls)
                finally:
                    hal.exitMain()

            th = threading.Thread(target=_start, name="RobotThread", daemon=True)
            th.start()
            try:
                hal.runMain()
            except KeyboardInterrupt:
                self.logger.exception(
                    "THIS IS NOT AN ERROR: The user hit CTRL-C to kill the robot"
                )
                self.logger.info("Exiting because of keyboard interrupt")

            self.suppressExitWarning = True
            robot = self.robot
            if robot:
                try:
                    robot.endCompetition()
                except:
                    self.logger.warn("endCompetition raised an exception")

            th.join(1)
            if th.is_alive():
                self.logger.warn("robot thread didn't die, crash may occur next!")
            return rval[0]
        else:
            return self.start(robot_cls)

    def start(self, robot_cls: wpilib.RobotBase) -> bool:
        try:
            return self._start(robot_cls)
        except:
            reportErrorInternal(
                "The robot program quit unexpectedly. This is usually due to a code error.\n"
                "The above stacktrace can help determine where the error occurred.\n",
            )
            return False

    def _start(self, robot_cls: wpilib.RobotBase) -> bool:

        import hal
        import wpilib

        hal.report(
            hal.tResourceType.kResourceType_Language,
            hal.tInstances.kLanguage_Python,
            0,
            wpilib.__version__,
        )

        if not wpilib.Notifier.setHALThreadPriority(True, 40):
            reportErrorInternal(
                "Setting HAL Notifier RT priority to 40 failed", isWarning=True
            )

        isSimulation = wpilib.RobotBase.isSimulation()

        # hack: initialize networktables before creating the robot
        #       class, otherwise our logger doesn't get created
        from _pyntcore import NetworkTables

        NetworkTables.setNetworkIdentity("Robot")
        if not isSimulation:
            NetworkTables.startServer("/home/lvuser/networktables.ini")
        else:
            NetworkTables.startServer()

        SmartDashboard.init()

        # Call DriverStation.inDisabled() to kick off DS thread
        wpilib.DriverStation.inDisabled(True)

        try:
            self.robot = robot_cls()
        except:
            reportError(
                f"Unhandled exception instantiating robot {robot_cls.__name__}", True
            )
            reportErrorInternal(f"Could not instantiate robot {robot_cls.__name__}!")
            raise

        # TODO: Add a check to see if the user forgot to call super().__init__()
        # if not hasattr(robot, "_RobotBase__initialized"):
        #     logger.error(
        #         "If your robot class has an __init__ function, it must call super().__init__()!"
        #     )
        #     return False

        if not isSimulation:
            try:
                with open("/tmp/frc_versions/FRC_Lib_Version.ini", "w") as fp:
                    fp.write("RobotPy %s" % wpilib.__version__)
            except:
                reportErrorInternal("Could not write FRC version file to disk")

        try:
            self.robot.startCompetition()
        except KeyboardInterrupt:
            self.robot = None
            self.logger.exception(
                "THIS IS NOT AN ERROR: The user hit CTRL-C to kill the robot"
            )
            self.logger.info("Exiting because of keyboard interrupt")
            return True
        except:
            self.robot = None

            reportError("Unhandled exception", True)
            raise
        else:
            self.robot = None
            if self.suppressExitWarning:
                self.logger.info("Robot code exited")
                return True
            else:
                # startCompetition never returns unless exception occurs....
                reportError("Unexpected return from startCompetition() method.", False)
                return False
