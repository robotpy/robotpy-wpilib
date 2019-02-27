# validated: 2018-09-09 EN 0614913f1abb edu/wpi/first/wpilibj/PWM.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import enum
from typing import Tuple

import hal
import weakref

from .motorsafety import MotorSafety
from .sendablebase import SendableBase
from .resource import Resource
from .sensorutil import SensorUtil
from .sendablebuilder import SendableBuilder

__all__ = ["PWM"]


def _freePWM(handle: hal.DigitalHandle) -> None:
    hal.setPWMDisabled(handle)
    hal.freePWMPort(handle)


class PWM(MotorSafety, SendableBase):
    """Raw interface to PWM generation in the FPGA.
    
    The values supplied as arguments for PWM outputs range from -1.0 to 1.0. They
    are mapped to the hardware dependent values, in this case 0-2000 for the
    FPGA.  Changes are immediately sent to the FPGA, and the update occurs at
    the next FPGA cycle (5.005 ms). There is no delay.

    As of revision 0.1.10 of the FPGA, the FPGA interprets the 0-2000 values as
    follows:
    
    - 2000 = full "forward"
    - 1999 to 1001 = linear scaling from "full forward" to "center"
    - 1000 = center value
    - 999 to 2 = linear scaling from "center" to "full reverse"
    - 1 = minimum pulse width (currently .5ms)
    - 0 = disabled (i.e. PWM output is held low)
    
    kDefaultPwmPeriod is the 1x period (5.05 ms).  In hardware, the period
    scaling is implemented as an output squelch to get longer periods for old
    devices.

    - 20ms periods (50 Hz) are the "safest" setting in that this works for all
      devices
    - 20ms periods seem to be desirable for Vex Motors
    - 20ms periods are the specified period for HS-322HD servos, but work
      reliably down to 10.0 ms; starting at about 8.5ms, the servo sometimes
      hums and get hot; by 5.0ms the hum is nearly continuous
    - 10ms periods work well for Victor 884
    - 5ms periods allows higher update rates for Luminary Micro Jaguar speed
      controllers. Due to the shipping firmware on the Jaguar, we can't run the
      update period less than 5.05 ms.
    """

    class PeriodMultiplier(enum.IntEnum):
        """Represents the amount to multiply the minimum servo-pulse pwm
        period by.
        """

        #: Period Multiplier: don't skip pulses. PWM pulses occur every 5.005 ms
        k1X = 1

        #: Period Multiplier: skip every other pulse. PWM pulses occur every 10.010 ms
        k2X = 2

        #: Period Multiplier: skip three out of four pulses. PWM pulses occur every 20.020 ms
        k4X = 4

    def __init__(self, channel: int) -> None:
        """Allocate a PWM given a channel.

        :param channel: The PWM channel number. 0-9 are on-board, 10-19 are on the MXP port
        """
        super().__init__()
        SendableBase.__init__(self)

        SensorUtil.checkPWMChannel(channel)
        self.channel = channel

        self.handle = hal.initializePWMPort(hal.getPort(channel))
        self.__finalizer = weakref.finalize(self, _freePWM, self.handle)

        self.setDisabled()

        hal.setPWMEliminateDeadband(self.handle, False)

        hal.report(hal.UsageReporting.kResourceType_PWM, channel)
        self.setName("PWM", channel)

        self.setSafetyEnabled(False)

        # Python-specific: Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

    def close(self) -> None:
        """Free the PWM channel.

        Free the resource associated with the PWM channel and set the value
        to 0.
        """
        super().close()
        if self.handle is None:
            return
        self.__finalizer()
        self.handle = None

    def stopMotor(self):
        self.setDisabled()

    def getDescription(self):
        return "PWM %d" % self.getChannel()

    def enableDeadbandElimination(self, eliminateDeadband: bool) -> None:
        """Optionally eliminate the deadband from a speed controller.

        :param eliminateDeadband: If True, set the motor curve on the Jaguar
            to eliminate the deadband in the middle of the range. Otherwise, keep
            the full range without modifying any values.
        """
        hal.setPWMEliminateDeadband(self.handle, eliminateDeadband)

    def setBounds(
        self,
        max: float,
        deadbandMax: float,
        center: float,
        deadbandMin: float,
        min: float,
    ) -> None:
        """Set the bounds on the PWM pulse widths.

        This sets the bounds on the PWM values for a particular type of
        controller.  The values determine the upper and lower speeds as well
        as the deadband bracket.

        :param max: The max PWM pulse width in ms
        :param deadbandMax: The high end of the deadband range pulse width in ms
        :param center: The center (off) pulse width in ms
        :param deadbandMin: The low end of the deadband pulse width in ms
        :param min: The minimum pulse width in ms
        """
        hal.setPWMConfig(self.handle, max, deadbandMax, center, deadbandMin, min)

    def getRawBounds(self) -> Tuple[int, int, int, int, int]:
        """Gets the bounds on the PWM pulse widths. This Gets the bounds on the PWM values for a
        particular type of controller. The values determine the upper and lower speeds as well
        as the deadband bracket.
        
        :returns: tuple of (max, deadbandMax, center, deadbandMin, min)
        """
        return hal.getPWMConfigRaw(self.handle)

    def getChannel(self) -> int:
        """Gets the channel number associated with the PWM Object.

        :returns: The channel number.
        """
        return self.channel

    def setPosition(self, pos: float) -> None:
        """Set the PWM value based on a position.

        This is intended to be used by servos.

        .. note::

            :func:`setBounds` must be called first.

        :param pos: The position to set the servo between 0.0 and 1.0.
        """
        hal.setPWMPosition(self.handle, pos)

    def getPosition(self) -> float:
        """Get the PWM value in terms of a position.

        This is intended to be used by servos.

        .. note::

            :func:`setBounds` must be called first.

        :returns: The position the servo is set to between 0.0 and 1.0.
        """
        return hal.getPWMPosition(self.handle)

    def setSpeed(self, speed: float) -> None:
        """Set the PWM value based on a speed.

        This is intended to be used by speed controllers.

        .. note::

            :func:`setBounds` must be called first.

        :param speed: The speed to set the speed controller between -1.0 and
            1.0.
        """
        hal.setPWMSpeed(self.handle, speed)

    def getSpeed(self) -> float:
        """Get the PWM value in terms of speed.

        This is intended to be used by speed controllers.

        .. note::

            :func:`setBounds` must be called first.

        :returns: The most recently set speed between -1.0 and 1.0.
        """
        return hal.getPWMSpeed(self.handle)

    def setRaw(self, value: int) -> None:
        """Set the PWM value directly to the hardware.

        Write a raw value to a PWM channel.

        :param value: Raw PWM value.  Range 0 - 255.
        """
        hal.setPWMRaw(self.handle, value)

    def getRaw(self) -> int:
        """Get the PWM value directly from the hardware.

        Read a raw value from a PWM channel.

        :returns: Raw PWM control value.  Range: 0 - 255.
        """
        return hal.getPWMRaw(self.handle)

    def setDisabled(self) -> None:
        """Temporarily disables the PWM output. The next set call will reenable
        the output.
        """
        hal.setPWMDisabled(self.handle)

    def setPeriodMultiplier(self, mult: PeriodMultiplier) -> None:
        """Slow down the PWM signal for old devices.

        :param mult: The period multiplier to apply to this channel
        """
        if mult == PWM.PeriodMultiplier.k4X:
            # Squelch 3 out of 4 outputs
            hal.setPWMPeriodScale(self.handle, 3)
        elif mult == PWM.PeriodMultiplier.k2X:
            # Squelch 1 out of 2 outputs
            hal.setPWMPeriodScale(self.handle, 1)
        elif mult == PWM.PeriodMultiplier.k1X:
            # Don't squelch any outputs
            hal.setPWMPeriodScale(self.handle, 0)
        else:
            raise ValueError("Invalid mult argument '%s'" % mult)

    def setZeroLatch(self) -> None:
        hal.latchPWMZero(self.handle)

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("PWM")
        builder.setSafeState(self.setDisabled)
        builder.addDoubleProperty(
            "Value", self.getRaw, lambda value: self.setRaw(int(value))
        )
