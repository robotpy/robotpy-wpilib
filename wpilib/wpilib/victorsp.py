from .talon import Talon

__all__ = ["VictorSP"]

class VictorSP(Talon):
    """
        Vex Robotics Victor SP Speed Controller
    """
    def __init__(self, channel):
        super().__init__(channel)
