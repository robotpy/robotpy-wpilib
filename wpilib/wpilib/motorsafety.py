# validated: 2019-01-02 DV f0f196e5b389 edu/wpi/first/wpilibj/MotorSafety.java
# ----------------------------------------------------------------------------
# Copyright (c) 2008-2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import logging
import threading
import weakref

from .timer import Timer

logger = logging.getLogger(__name__)

__all__ = ["MotorSafety"]


class MotorSafety:
    """Provides mechanisms to safely shutdown motors if they aren't updated
    often enough.

    This base class runs a watchdog timer and calls the subclass's stopMotor()
    function if the timeout expires.

    The subclass should call feed() whenever the motor value is updated.
    """

    DEFAULT_SAFETY_EXPIRATION = 0.1
    __instanceList = weakref.WeakSet()
    __listMutex = threading.Lock()

    @classmethod
    def _reset(cls) -> None:
        with cls.__listMutex:
            cls.__instanceList.clear()

    def __init__(self) -> None:
        self.__enabled = False
        self.__expiration = self.DEFAULT_SAFETY_EXPIRATION
        self.__stopTime = Timer.getFPGATimestamp()
        self.__mutex = threading.Lock()
        with self.__listMutex:
            self.__instanceList.add(self)

    def feed(self) -> None:
        """Feed the motor safety object.

        Resets the timer on this object that is used to do the timeouts.
        """
        with self.__mutex:
            self.__stopTime = Timer.getFPGATimestamp() + self.__expiration

    def setExpiration(self, expirationTime: float) -> None:
        """Set the expiration time for the corresponding motor safety object.

        :param expirationTime: The timeout value in seconds.
        """
        with self.__mutex:
            self.__expiration = expirationTime

    def getExpiration(self) -> float:
        """Retrieve the timeout value for the corresponding motor safety object.

        :returns: the timeout value in seconds.
        """
        with self.__mutex:
            return self.__expiration

    def isAlive(self) -> bool:
        """Determine of the motor is still operating or has timed out.

        :returns: True if the motor is still operating normally and hasn't
            timed out.
        """
        with self.__mutex:
            return not self.__enabled or self.__stopTime > Timer.getFPGATimestamp()

    def check(self) -> None:
        """Check if this motor has exceeded its timeout.
        This method is called periodically to determine if this motor has
        exceeded its timeout value. If it has, the stop method is called,
        and the motor is shut down until its value is updated again.
        """
        from .robotstate import RobotState

        with self.__mutex:
            enabled = self.__enabled
            stopTime = self.__stopTime

        if not enabled or RobotState.isDisabled() or RobotState.isTest():
            return

        if stopTime < Timer.getFPGATimestamp():
            # TODO: fix this, causes recursion error
            logger.warning(
                "%s... Output not updated often enough." % self.getDescription()
            )

            self.stopMotor()

    def setSafetyEnabled(self, enabled: bool) -> None:
        """Enable/disable motor safety for this device.

        Turn on and off the motor safety option for this PWM object.

        :param enabled: True if motor safety is enforced for this object
        """
        with self.__mutex:
            self.__enabled = bool(enabled)

    def isSafetyEnabled(self) -> bool:
        """Return the state of the motor safety enabled flag.

        Return if the motor safety is currently enabled for this device.

        :returns: True if motor safety is enforced for this device
        """
        with self.__mutex:
            return self.__enabled

    @classmethod
    def checkMotors(cls) -> None:
        """Check the motors to see if any have timed out.
        This static method is called periodically to poll all the motors and
        stop any that have timed out.
        """
        with cls.__listMutex:
            for elem in cls.__instanceList:
                elem.check()

    # abstract methods

    def stopMotor(self) -> None:
        raise NotImplementedError

    def getDescription(self) -> str:
        raise NotImplementedError
