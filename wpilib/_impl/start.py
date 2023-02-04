import hal
import wpilib
import logging
import threading
import time

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
        retval = False
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
            retval = rval[0]
        else:
            retval = self.start(robot_cls)

        from wpilib import RobotBase

        if RobotBase.isSimulation():
            import wpilib.simulation

            wpilib.simulation._simulation._resetMotorSafety()

        return retval

    def start(self, robot_cls: wpilib.RobotBase) -> bool:
        try:
            return self._start(robot_cls)
        except:
            reportErrorInternal(
                "The robot program quit unexpectedly. This is usually due to a code error.\n"
                "The above stacktrace can help determine where the error occurred.\n",
                True,
            )
            return False

    def _start(self, robot_cls: wpilib.RobotBase) -> bool:
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
        import ntcore

        inst = ntcore.NetworkTableInstance.getDefault()

        # subscribe to "" to force persistent values to progagate to local
        msub = ntcore.MultiSubscriber(inst, [""])

        if not isSimulation:
            inst.startServer("/home/lvuser/networktables.ini")
        else:
            inst.startServer()

        # wait for the NT server to actually start
        for i in range(100):
            if (
                inst.getNetworkMode()
                & ntcore.NetworkTableInstance.NetworkMode.kNetModeStarting
            ) == 0:
                break
            # real sleep since we're waiting for the server, not simulated sleep
            time.sleep(0.010)
        else:
            reportErrorInternal(
                "timed out while waiting for NT server to start", isWarning=True
            )

        wpilib.SmartDashboard.init()

        # Call DriverStation.refreshData() to kick things off
        wpilib.DriverStation.refreshData()

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
                from robotpy.version import __version__ as robotpy_version

                version_string = f"RobotPy {robotpy_version}"
            except ImportError:
                version_string = f"robotpy-wpilib {wpilib.__version__}"

            try:
                with open("/tmp/frc_versions/FRC_Lib_Version.ini", "w") as fp:
                    fp.write(version_string)
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
