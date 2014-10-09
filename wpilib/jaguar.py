#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .safepwm import SafePWM

class Jaguar(SafePWM):
    """Texas Instruments Jaguar Speed Controller as a PWM device."""

    def __init__(self, channel):
        """Constructor.

        :param channel: The PWM channel that the Jaguar is attached to.
        """
        super().__init__(channel)
        # Input profile defined by Luminary Micro.
        #
        # Full reverse ranges from 0.671325ms to 0.6972211ms
        # Proportional reverse ranges from 0.6972211ms to 1.4482078ms
        # Neutral ranges from 1.4482078ms to 1.5517922ms
        # Proportional forward ranges from 1.5517922ms to 2.3027789ms
        # Full forward ranges from 2.3027789ms to 2.328675ms
        self.setBounds(2.31, 1.55, 1.507, 1.454, 0.697)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setRaw(self.centerPwm)
        self.setZeroLatch()

        hal.HALReport(hal.HALUsageReporting.kResourceType_Jaguar,
                      self.getChannel())
        LiveWindow.addActuatorChannel("Jaguar", self.getChannel(), self)

    def set(self, speed, syncGroup=0):
        """Set the PWM value.

        The PWM value is set using a range of -1.0 to 1.0, appropriately
        scaling the value for the FPGA.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :param syncGroup: The update group to add this set() to, pending
            updateSyncGroup().  If 0, update immediately.
        """
        self.setSpeed(speed)
        self.feed()

    def get(self):
        """Get the recently set value of the PWM.

        :returns: The most recently set value for the PWM between -1.0 and 1.0.
        """
        return self.getSpeed()

    def pidWrite(self, output):
        """Write out the PID value as seen in the PIDOutput base object.

        :param output: Write out the PWM value as was found in the
            :class:`PIDController`.
        """
        self.set(output)
