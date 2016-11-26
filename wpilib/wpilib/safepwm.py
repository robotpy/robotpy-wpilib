# validated: 2016-11-26 DS 5ad28d58ec63 athena/java/edu/wpi/first/wpilibj/SafePWM.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .motorsafety import MotorSafety
from .pwm import PWM

__all__ = ["SafePWM"]

class SafePWM(PWM, MotorSafety):
    """
        A raw PWM interface that implements the :class:`.MotorSafety` interface
    """
    
    def __init__(self, channel):
        """Constructor for a SafePWM object taking a channel number.

        :param channel: The channel number to be used for the underlying PWM
            object. 0-9 are on-board, 10-19 are on the MXP port.
        :type  channel: int
        """
        MotorSafety.__init__(self)
        PWM.__init__(self, channel)
        self.setExpiration(0.0)
        self.setSafetyEnabled(False)

    def stopMotor(self):
        """Stop the motor associated with this PWM object.
        This is called by the MotorSafety object when it has a timeout for
        this PWM and needs to stop it from running.
        """
        self.disable()

    def getDescription(self):
        return "PWM %d" % self.getChannel()

    def disable(self):
        self.setDisabled()
