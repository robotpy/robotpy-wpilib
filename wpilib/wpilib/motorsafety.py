# validated: 2018-12-18 n 26e8e587f926 edu/wpi/first/wpilibj/MotorSafety.java
# ----------------------------------------------------------------------------
# Copyright (c) 2008-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import logging
import threading
import weakref

from .robotstate import RobotState
from .timer import Timer
from .watchdog import Watchdog
from .driverstation import DriverStation

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
        self.watchdog = Watchdog(MotorSafety.DEFAULT_SAFETY_EXPIRATION, ) # todo timeout function
        self.mutex = threading.Lock()
        with MotorSafety.helpers_lock:
            MotorSafety.helpers.add(self)

    def feed(self):
        """Feed the motor safety object.
        Resets the timer on this object that is used to do the timeouts.
        """
        with self.mutex:
            self.watchdog.reset()

    def setExpiration(self, expirationTime):
        """Set the expiration time for the corresponding motor safety object.

        :param expirationTime: The timeout value in seconds.
        :type expirationTime: float
        """
        with self.mutex:
            self.watchdog.timeout = expirationTime

    def getExpiration(self):
        """Retrieve the timeout value for the corresponding motor safety
        object.

        :returns: the timeout value in seconds.
        :rtype: float
        """
        with self.mutex:
            return self.watchdog.timeout

    def isAlive(self):
        """Determine of the motor is still operating or has timed out.

        :returns: True if the motor is still operating normally and hasn't
            timed out.
        :rtype: float
        """
        with self.mutex:
            return (
                not self.safetyEnabled or self.watchdog.isExpired()
            )

    def setSafetyEnabled(self, enabled):
        """Enable/disable motor safety for this device.
        Turn on and off the motor safety option for this PWM object.

        :param enabled: True if motor safety is enforced for this object
        :type  enabled: bool
        """
        with self.mutex:
            self.safetyEnabled = bool(enabled)
            if self.safetyEnabled:
                self.watchdog.enable()
            else:
                self.watchdog.disable()

    def isSafetyEnabled(self):
        """Return the state of the motor safety enabled flag.
        Return if the motor safety is currently enabled for this device.

        :returns: True if motor safety is enforced for this device
        :rtype: bool
        """
        with self.mutex:
            return self.safetyEnabled

    def timeoutFunc(self):
        ds = DriverStation.getInstance()

        if ds.isDisabled() or ds.isTest():
            return None

        DriverStation.reportError(self.getDescription() + "... Output not updated often enough.", False)
        self.stopMotor()
