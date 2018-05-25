# validated: 2017-12-12 EN f9bece2ffbf7 edu/wpi/first/wpilibj/Servo.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .livewindow import LiveWindow
from .pwm import PWM
from .sendablebuilder import SendableBuilder

__all__ = ["Servo"]


class Servo(PWM):
    """Standard hobby style servo

    The range parameters default to the appropriate values for the Hitec
    HS-322HD servo provided in the FIRST Kit of Parts in 2008.
    """

    kMaxServoAngle = 180.0
    kMinServoAngle = 0.0

    kDefaultMaxServoPWM = 2.4
    kDefaultMinServoPWM = 0.6

    def __init__(self, channel: int) -> None:
        """Constructor.

        * By default `kDefaultMaxServoPWM` ms is used as the maxPWM value
        * By default `kDefaultMinServoPWM` ms is used as the minPWM value

        :param channel: The PWM channel to which the servo is attached. 0-9 are on-board, 10-19 are on the MXP port.
        """
        super().__init__(channel)
        self.setBounds(self.kDefaultMaxServoPWM, 0, 0, 0, self.kDefaultMinServoPWM)
        self.setPeriodMultiplier(self.PeriodMultiplier.k4X)

        self.valueEntry = None
        self.valueListener = None

        hal.report(hal.UsageReporting.kResourceType_Servo, self.getChannel())
        self.setName("Servo", self.getChannel())

    def set(self, value: float) -> None:
        """Set the servo position.

        Servo values range from 0.0 to 1.0 corresponding to the range of
        full left to full right.

        :param value: Position from 0.0 to 1.0.
        """
        self.setPosition(value)

    def get(self) -> float:
        """Get the servo position.

        Servo values range from 0.0 to 1.0 corresponding to the range of
        full left to full right.

        :returns: Position from 0.0 to 1.0.
        """
        return self.getPosition()

    def setAngle(self, degrees: float) -> None:
        """Set the servo angle.

        Assumes that the servo angle is linear with respect to the PWM value
        (big assumption, need to test).

        Servo angles that are out of the supported range of the servo simply
        "saturate" in that direction In other words, if the servo has a range
        of (X degrees to Y degrees) than angles of less than X result in an
        angle of X being set and angles of more than Y degrees result in an
        angle of Y being set.

        :param degrees: The angle in degrees to set the servo.
        """
        if degrees < self.kMinServoAngle:
            degrees = self.kMinServoAngle
        elif degrees > self.kMaxServoAngle:
            degrees = self.kMaxServoAngle

        self.setPosition(((degrees - self.kMinServoAngle)) / self.getServoAngleRange())

    def getAngle(self) -> float:
        """Get the servo angle.

        Assume that the servo angle is linear with respect to the PWM value
        (big assumption, need to test).

        :returns: The angle in degrees to which the servo is set.
        """
        return self.getPosition() * self.getServoAngleRange() + self.kMinServoAngle

    def getServoAngleRange(self) -> float:
        return self.kMaxServoAngle - self.kMinServoAngle

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Servo")
        builder.addDoubleProperty("Value", self.get, self.set)
