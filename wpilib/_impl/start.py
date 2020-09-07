import hal
import wpilib
import logging
import threading


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
            hal.runMain()
            self.suppressExitWarning = True
            if self.robot:
                try:
                    self.robot.endCompetition()
                except:
                    self.logger.warn("endCompetition raised an exception")

            th.join(1)
            if th.is_alive():
                self.logger.warn("robot thread didn't die, crash may occur next!")
        else:
            return self.start(robot_cls)

    def start(self, robot_cls: wpilib.RobotBase) -> bool:

        import hal
        import wpilib

        DriverStation = wpilib.DriverStation

        hal.report(
            hal.tResourceType.kResourceType_Language,
            hal.tInstances.kLanguage_Python,
            0,
            wpilib.__version__,
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

        try:
            self.robot = robot_cls()
        except:
            DriverStation.reportError(
                "Unhandled exception instantiating robot " + robot_cls.__name__, True
            )
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError(
                "Could not instantiate robot " + robot_cls.__name__ + "!", False
            )
            return False

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
                DriverStation.reportError(
                    "Could not write FRC version file to disk", True
                )

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

            DriverStation.reportError("Unhandled exception", True)
            DriverStation.reportWarning("Robots should not quit, but yours did!", False)
            DriverStation.reportError(
                "The startCompetition() method (or methods called by it) should have handled the exception above.",
                False,
            )
            return False
        else:
            self.robot = None
            if self.suppressExitWarning:
                self.logger.info("Robot code exited")
                return True
            else:
                # startCompetition never returns unless exception occurs....
                DriverStation.reportWarning(
                    "Robots should not quit, but yours did!", False
                )
                DriverStation.reportError(
                    "Unexpected return from startCompetition() method.", False
                )
                return False
