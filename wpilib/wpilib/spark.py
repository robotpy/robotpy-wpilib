# validated: 2016-11-26 DS e44a6e227a89 athena/java/edu/wpi/first/wpilibj/Spark.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .pwmspeedcontroller import PWMSpeedController

__all__ = ["Spark"]

class Spark(PWMSpeedController):
    """
        REV Robotics SPARK Speed Controller
           
        .. not_implemented: initSpark
    """

    def __init__(self, channel):
        """Constructor.

        :param channel: The PWM channel that the SPARK is attached to. 0-9 are on-board, 10-19 are on the MXP port
        
        .. note ::
        
           Note that the SD540 uses the following bounds for PWM values. These
           values should work reasonably well for most controllers, but if users
           experience issues such as asymmetric behavior around the deadband or
           inability to saturate the controller in either direction, calibration is
           recommended. The calibration procedure can be found in the SD540 User
           Manual available from Mindsensors.
           
           - 2.003ms = full "forward"
           - 1.55ms = the "high end" of the deadband range
           - 1.50ms = center of the deadband range (off)
           - 1.46ms = the "low end" of the deadband range
           - .999ms = full "reverse"
        
        """
        super().__init__(channel)
        self.setBounds(2.003, 1.55, 1.50, 1.46, .999)
        self.setPeriodMultiplier(self.PeriodMultiplier.k1X)
        self.setSpeed(0)
        self.setZeroLatch()

        LiveWindow.addActuatorChannel("Spark", self.getChannel(), self)
        hal.report(hal.UsageReporting.kResourceType_RevSPARK,
                   self.getChannel())
