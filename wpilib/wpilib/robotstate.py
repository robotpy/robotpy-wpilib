# validated: 2018-01-04 TW e1195e8b9dab edu/wpi/first/wpilibj/RobotState.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016-2018. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .driverstation import DriverStation

__all__ = ["RobotState"]


class RobotState:
    """Provides an interface to determine the current operating state of the
    robot code.
    """

    @staticmethod
    def isDisabled() -> bool:
        return DriverStation.getInstance().isDisabled()

    @staticmethod
    def isEnabled() -> bool:
        return DriverStation.getInstance().isEnabled()

    @staticmethod
    def isOperatorControl() -> bool:
        return DriverStation.getInstance().isOperatorControl()

    @staticmethod
    def isAutonomous() -> bool:
        return DriverStation.getInstance().isAutonomous()

    @staticmethod
    def isTest() -> bool:
        return DriverStation.getInstance().isTest()
