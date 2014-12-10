from .talon import Talon

__all__ = ["TalonSRX"]

class TalonSRX(Talon):
    """
        Cross the Road Electronics (CTRE) Talon SRX Speed Controller with PWM
        control.  See CANTalon for CAN control of Talon SRX.
    """

    def __init__(self, channel):
        """Constructor.

        :param channel: The PWM channel that the Talon SRX is attached to.

        """
        super().__init__(channel)
