# validated: 2016-11-26 DS e44a6e227a89 athena/java/edu/wpi/first/wpilibj/Servo.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .pwm import PWM

__all__ = ["Servo"]

class Servo(PWM):
    """Standard hobby style servo

    The range parameters default to the appropriate values for the Hitec
    HS-322HD servo provided in the FIRST Kit of Parts in 2008.
    """

    kMaxServoAngle = 180.0
    kMinServoAngle = 0.0

    kDefaultMaxServoPWM = 2.4
    kDefaultMinServoPWM = .6

    def __init__(self, channel):
        """Constructor.

        * By default `kDefaultMaxServoPWM` ms is used as the maxPWM value
        * By default `kDefaultMinServoPWM` ms is used as the minPWM value

        :param channel: The PWM channel to which the servo is attached. 0-9 are on-board, 10-19 are on the MXP port.
        :type  channel: int
        """
        super().__init__(channel)
        self.setBounds(self.kDefaultMaxServoPWM, 0, 0, 0,
                       self.kDefaultMinServoPWM)
        self.setPeriodMultiplier(self.PeriodMultiplier.k4X)

        LiveWindow.addActuatorChannel("Servo", self.getChannel(), self)
        hal.report(hal.UsageReporting.kResourceType_Servo,
                   self.getChannel())

    def free(self):
        LiveWindow.removeComponent(self)
        super().free()

    def set(self, value):
        """Set the servo position.

        Servo values range from 0.0 to 1.0 corresponding to the range of
        full left to full right.

        :param value: Position from 0.0 to 1.0.
        :type  value: float
        """
        self.setPosition(value)

    def get(self):
        """Get the servo position.

        Servo values range from 0.0 to 1.0 corresponding to the range of
        full left to full right.

        :returns: Position from 0.0 to 1.0.
        :rtype: float
        """
        return self.getPosition()

    def setAngle(self, degrees):
        """Set the servo angle.

        Assumes that the servo angle is linear with respect to the PWM value
        (big assumption, need to test).

        Servo angles that are out of the supported range of the servo simply
        "saturate" in that direction In other words, if the servo has a range
        of (X degrees to Y degrees) than angles of less than X result in an
        angle of X being set and angles of more than Y degrees result in an
        angle of Y being set.

        :param degrees: The angle in degrees to set the servo.
        :type  degrees: float
        """
        if degrees < self.kMinServoAngle:
            degrees = self.kMinServoAngle
        elif degrees > self.kMaxServoAngle:
            degrees = self.kMaxServoAngle

        self.setPosition(((degrees - self.kMinServoAngle)) /
                         self.getServoAngleRange())

    def getAngle(self):
        """Get the servo angle.

        Assume that the servo angle is linear with respect to the PWM value
        (big assumption, need to test).

        :returns: The angle in degrees to which the servo is set.
        :rtype: float
        """
        return self.getPosition() * self.getServoAngleRange() + self.kMinServoAngle

    def getServoAngleRange(self):
        return self.kMaxServoAngle - self.kMinServoAngle

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Servo"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.get())

    def valueChanged(self, itable, key, value, bln):
        self.set(float(value))
