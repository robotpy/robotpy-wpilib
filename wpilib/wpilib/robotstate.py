# validated: 2018-01-04 TW e1195e8b9dab edu/wpi/first/wpilibj/RobotState.java

__all__ = ["RobotState"]

class RobotState:
    """Provides an interface to determine the current operating state of the
    robot code.
    """
    
    impl = None

    @staticmethod
    def isDisabled():
        return RobotState.impl.isDisabled()

    @staticmethod
    def isEnabled():
        return RobotState.impl.isEnabled()

    @staticmethod
    def isOperatorControl():
        return RobotState.impl.isOperatorControl()

    @staticmethod
    def isAutonomous():
        return RobotState.impl.isAutonomous()

    @staticmethod
    def isTest():
        return RobotState.impl.isTest()
