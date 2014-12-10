from .talon import Talon

__all__ = ["VictorSP"]

class VictorSP(Talon):
    """
        Vex Robotics Victor SP Speed Controller
    """

    def __init__(self, channel):
        """Constructor.

        :param channel: The PWM channel that the VictorSP is attached to.

        """
        super().__init__(channel)
