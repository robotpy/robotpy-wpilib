# validated: 2016-11-26 DS 952ebb11adfe shared/java/edu/wpi/first/wpilibj/MotorSafety.java athena/java/edu/wpi/first/wpilibj/MotorSafetyHelper.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import weakref
import threading

from .robotstate import RobotState
from .timer import Timer

import logging
logger = logging.getLogger(__name__)

__all__ = ["MotorSafety"]

class MotorSafety:
    """Provides mechanisms to safely shutdown motors if they aren't updated
    often enough.
    
    The MotorSafety object is constructed for every object that wants to
    implement the Motor Safety protocol. The helper object has the code to
    actually do the timing and call the motors stop() method when the timeout
    expires. The motor object is expected to call the feed() method whenever
    the motors value is updated.
    
    .. robotpy-specific:: In the Java implementation this is MotorSafetyHelper
    """
    DEFAULT_SAFETY_EXPIRATION = 0.1
    helpers = weakref.WeakSet()
    helpers_lock = threading.Lock()
    
    @staticmethod
    def _reset():
        with MotorSafety.helpers_lock:
            MotorSafety.helpers.clear()

    def __init__(self):
        """The constructor for a MotorSafety object.
        The helper object is constructed for every object that wants to
        implement the Motor Safety protocol. The helper object has the code
        to actually do the timing and call the motors stop() method when the
        timeout expires. The motor object is expected to call the feed()
        method whenever the motors value is updated.
        """
        self.safetyEnabled = False
        self.safetyExpiration = MotorSafety.DEFAULT_SAFETY_EXPIRATION
        self.safetyStopTime = Timer.getFPGATimestamp()
        with MotorSafety.helpers_lock:
            MotorSafety.helpers.add(self)

    def feed(self):
        """Feed the motor safety object.
        Resets the timer on this object that is used to do the timeouts.
        """
        self.safetyStopTime = Timer.getFPGATimestamp() + self.safetyExpiration

    def setExpiration(self, expirationTime):
        """Set the expiration time for the corresponding motor safety object.

        :param expirationTime: The timeout value in seconds.
        :type expirationTime: float
        """
        self.safetyExpiration = expirationTime

    def getExpiration(self):
        """Retrieve the timeout value for the corresponding motor safety
        object.

        :returns: the timeout value in seconds.
        :rtype: float
        """
        return self.safetyExpiration

    def isAlive(self):
        """Determine of the motor is still operating or has timed out.

        :returns: True if the motor is still operating normally and hasn't
            timed out.
        :rtype: float
        """
        return not self.safetyEnabled or self.safetyStopTime > Timer.getFPGATimestamp()

    def check(self):
        """Check if this motor has exceeded its timeout.
        This method is called periodically to determine if this motor has
        exceeded its timeout value. If it has, the stop method is called,
        and the motor is shut down until its value is updated again.
        """
        if not self.safetyEnabled or RobotState.isDisabled() or RobotState.isTest():
            return
        if self.safetyStopTime < Timer.getFPGATimestamp():
            logger.warn("%s... Output not updated often enough." %
                        self.getDescription())

            self.stopMotor()

    def setSafetyEnabled(self, enabled):
        """Enable/disable motor safety for this device.
        Turn on and off the motor safety option for this PWM object.

        :param enabled: True if motor safety is enforced for this object
        :type  enabled: bool
        """
        self.safetyEnabled = bool(enabled)

    def isSafetyEnabled(self):
        """Return the state of the motor safety enabled flag.
        Return if the motor safety is currently enabled for this device.

        :returns: True if motor safety is enforced for this device
        :rtype: bool
        """
        return self.safetyEnabled

    @staticmethod
    def checkMotors():
        """Check the motors to see if any have timed out.
        This static method is called periodically to poll all the motors and
        stop any that have timed out.
        """
        with MotorSafety.helpers_lock:
            for msh in MotorSafety.helpers:
                msh.check()
