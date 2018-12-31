# validated: 2018-01-04 TW e1195e8b9dab edu/wpi/first/wpilibj/RobotState.java

__all__ = ["RobotState"]


class RobotState:
    """Provides an interface to determine the current operating state of the
    robot code.
    """

    impl = None

    @staticmethod
    def isDisabled() -> bool:
        return RobotState.impl.isDisabled()

    @staticmethod
    def isEnabled() -> bool:
        return RobotState.impl.isEnabled()

    @staticmethod
    def isOperatorControl() -> bool:
        return RobotState.impl.isOperatorControl()

    @staticmethod
    def isAutonomous() -> bool:
        return RobotState.impl.isAutonomous()

    @staticmethod
    def isTest() -> bool:
        return RobotState.impl.isTest()
