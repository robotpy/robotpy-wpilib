class RobotState:
    impl = None

    @staticmethod
    def isDisabled():
        return impl.isDisabled()

    @staticmethod
    def isEnabled():
        return impl.isEnabled()

    @staticmethod
    def isOperatorControl():
        return impl.isOperatorControl()

    @staticmethod
    def isAutonomous():
        return impl.isAutonomous()

    @staticmethod
    def isTest():
        return impl.isTest()
