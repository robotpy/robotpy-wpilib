# validated: 2016-11-26 DS 9e99df1cf70a athena/java/edu/wpi/first/wpilibj/PWMSpeedController.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .livewindow import LiveWindow
from .safepwm import SafePWM

__all__ = ["PWMSpeedController"]

class PWMSpeedController(SafePWM):
    """
        Common base class for all PWM Speed Controllers.
    """
    
    def __init__(self, channel):
        super().__init__(channel)
        self.isInverted = False
    
    def free(self):
        LiveWindow.removeComponent(self)
        super().free()

    def set(self, speed):
        """Set the PWM value.

        The PWM value is set using a range of -1.0 to 1.0, appropriately
        scaling the value for the FPGA.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :type  speed: float
        """
        self.setSpeed(-speed if self.isInverted else speed)
        self.feed()

    def setInverted(self, isInverted):
        """
        Common interface for inverting the direction of a speed controller.

        :param isInverted: The state of inversion (True is inverted).
        """
        self.isInverted = isInverted

    def getInverted(self):
        """
        Common interface for inverting the direction of a speed controller.

        :returns: The state of inversion (True is inverted)
        """
        return self.isInverted

    def get(self):
        """Get the recently set value of the PWM.

        :returns: The most recently set value for the PWM between -1.0 and 1.0.
        :rtype: float
        """
        return self.getSpeed()

    def pidWrite(self, output):
        """Write out the PID value as seen in the PIDOutput base object.

        :param output: Write out the PWM value as was found in the
            :class:`PIDController`.
        :type  output: float
        """
        self.set(output)
