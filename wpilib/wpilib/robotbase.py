# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.

import hal

class RobotBase:
    """Implement a Robot Program framework.
    The RobotBase class is intended to be subclassed by a user creating a
    robot program.  Overridden autonomous() and operatorControl() methods
    are called at the appropriate time as the match proceeds. In the current
    implementation, the Autonomous code will run to completion before the
    OperatorControl code could start. In the future the Autonomous code might
    be spawned as a task, then killed at the end of the Autonomous period.
    """

    def __init__(self):
        """Constructor for a generic robot program.
        User code should be placed in the constructor that runs before the
        Autonomous or Operator Control period starts. The constructor will
        run to completion before Autonomous is entered.

        This must be used to ensure that the communications code starts. In
        the future it would be nice to put this code into it's own task that
        loads on boot so ensure that it runs.
        """
        # TODO: StartCAPI();
        # TODO: See if the next line is necessary
        # Resource.RestartProgram()

        #TODO:from .networktables import NetworkTable
        #TODO:NetworkTable.setServerMode()#must be before b

        from .driverstation import DriverStation
        self.ds = DriverStation.getInstance()

        #TODO:NetworkTable.getTable("")   # forces network tables to initialize
        #TODO:NetworkTable.getTable("LiveWindow").getSubTable("~STATUS~").putBoolean("LW Enabled", False)

    def free(self):
        """Free the resources for a RobotBase class."""
        # TODO: delete?
        pass

    @staticmethod
    def isSimulation():
        """:returns: If the robot is running in simulation."""
        return False

    @staticmethod
    def isReal():
        """:returns: If the robot is running in the real world."""
        return True

    def isDisabled(self):
        """Determine if the Robot is currently disabled.

        :returns: True if the Robot is currently disabled by the field
            controls.
        """
        return self.ds.isDisabled()

    def isEnabled(self):
        """Determine if the Robot is currently enabled.

        :returns: True if the Robot is currently enabled by the field
            controls.
        """
        return self.ds.isEnabled()

    def isAutonomous(self):
        """Determine if the robot is currently in Autonomous mode.

        :returns: True if the robot is currently operating Autonomously as
            determined by the field controls.
        """
        return self.ds.isAutonomous()

    def isTest(self):
        """Determine if the robot is currently in Test mode.

        :returns: True if the robot is currently operating in Test mode as
            determined by the driver station.
        """
        return self.ds.isTest()

    def isOperatorControl(self):
        """Determine if the robot is currently in Operator Control mode.

        :returns: True if the robot is currently operating in Tele-Op mode as
        determined by the field controls.
        """
        return self.ds.isOperatorControl()

    def isNewDataAvailable(self):
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
        hal.HALInitialize()
        hal.HALNetworkCommunicationObserveUserProgramStarting()

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
        except:
            print("WARNING: Robots don't quit!")
            print("ERROR: Could not instantiate robot "+robot_cls.__name__+"!")
            raise

        try:
            robot.startCompetition()
        except:
            print("WARNING: Robots don't quit!")
            print("---> The startCompetition() method (or methods called by it) should have handled the exception.")
            raise
        else:
            # startCompetition never returns unless exception occurs....
            print("WARNING: Robots don't quit!");
            print("---> Unexpected return from startCompetition() method.")
