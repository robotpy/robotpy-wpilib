#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref

from .livewindowsendable import LiveWindowSendable
from .resource import Resource
from .sensorbase import SensorBase

__all__ = ["PWM"]

def _freePWM(port):
    hal.setPWM(port, 0)
    hal.freePWMChannel(port)
    hal.freeDIO(port)

class PWM(LiveWindowSendable):
    """Raw interface to PWM generation in the FPGA.
    
    The values supplied as arguments for PWM outputs range from -1.0 to 1.0. They
    are mapped to the hardware dependent values, in this case 0-2000 for the
    FPGA.  Changes are immediately sent to the FPGA, and the update occurs at
    the next FPGA cycle. There is no delay.

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
      
    .. not_implemented: initPWM
    """
    class PeriodMultiplier:
        """Represents the amount to multiply the minimum servo-pulse pwm
        period by.
        """
        k1X = 1
        k2X = 2
        k4X = 4

    #: the default PWM period measured in ms.
    kDefaultPwmPeriod = 5.05
    
    #: the PWM range center in ms
    kDefaultPwmCenter = 1.5
    
    #: the number of PWM steps below the centerpoint
    kDefaultPwmStepsDown = 1000
    
    #: the value to use to disable
    kPwmDisabled = 0

    def __init__(self, channel):
        """Allocate a PWM given a channel.

        :param channel: The PWM channel number. 0-9 are on-board, 10-19 are on the MXP port
        :type channel: int
        """
        SensorBase.checkPWMChannel(channel)
        self.channel = channel
        self._port = hal.initializeDigitalPort(hal.getPort(channel))

        if not hal.allocatePWMChannel(self._port):
            raise IndexError("PWM channel %d is already allocated" % channel)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        hal.setPWM(self._port, 0)

        self._pwm_finalizer = weakref.finalize(self, _freePWM, self._port)

        self.eliminateDeadband = False

        hal.HALReport(hal.HALUsageReporting.kResourceType_PWM, channel)

    @property
    def port(self):
        if not self._pwm_finalizer.alive:
            return None
        return self._port

    def free(self):
        """Free the PWM channel.

        Free the resource associated with the PWM channel and set the value
        to 0.
        """
        self._pwm_finalizer()

    def enableDeadbandElimination(self, eliminateDeadband):
        """Optionally eliminate the deadband from a speed controller.

        :param eliminateDeadband: If True, set the motor curve on the Jaguar
            to eliminate the deadband in the middle of the range. Otherwise, keep
            the full range without modifying any values.
        :type eliminateDeadband: bool
        """
        self.eliminateDeadband = eliminateDeadband

    def setBounds(self, max, deadbandMax, center, deadbandMin, min):
        """Set the bounds on the PWM pulse widths.

        This sets the bounds on the PWM values for a particular type of
        controller.  The values determine the upper and lower speeds as well
        as the deadband bracket.

        :param max: The max PWM pulse width in ms
        :type max: float
        :param deadbandMax: The high end of the deadband range pulse width in ms
        :type deadbandMax: float
        :param center: The center (off) pulse width in ms
        :type center: float
        :param deadbandMin: The low end of the deadband pulse width in ms
        :type deadbandMin: float
        :param min: The minimum pulse width in ms
        :type min: float
        """
        loopTime = hal.getLoopTiming()/(SensorBase.kSystemClockTicksPerMicrosecond*1e3)

        self.maxPwm = int((max-self.kDefaultPwmCenter)/loopTime+self.kDefaultPwmStepsDown-1)
        self.deadbandMaxPwm = int((deadbandMax-self.kDefaultPwmCenter)/loopTime+self.kDefaultPwmStepsDown-1)
        self.centerPwm = int((center-self.kDefaultPwmCenter)/loopTime+self.kDefaultPwmStepsDown-1)
        self.deadbandMinPwm = int((deadbandMin-self.kDefaultPwmCenter)/loopTime+self.kDefaultPwmStepsDown-1)
        self.minPwm = int((min-self.kDefaultPwmCenter)/loopTime+self.kDefaultPwmStepsDown-1)

    def getChannel(self):
        """Gets the channel number associated with the PWM Object.

        :returns: The channel number.
        :rtype: int
        """
        return self.channel

    def setPosition(self, pos):
        """Set the PWM value based on a position.

        This is intended to be used by servos.

        .. note::

            :func:`setBounds` must be called first.

        :param pos: The position to set the servo between 0.0 and 1.0.
        :type pos: float
        """
        if pos < 0.0:
            pos = 0.0
        elif pos > 1.0:
            pos = 1.0

        rawValue = int(pos * self.getFullRangeScaleFactor() + self.getMinNegativePwm())

        # send the computed pwm value to the FPGA
        self.setRaw(rawValue)

    def getPosition(self):
        """Get the PWM value in terms of a position.

        This is intended to be used by servos.

        .. note::

            :func:`setBounds` must be called first.

        :returns: The position the servo is set to between 0.0 and 1.0.
        :rtype: float
        """
        value = self.getRaw()
        if value < self.getMinNegativePwm():
            return 0.0
        elif value > self.getMaxPositivePwm():
            return 1.0
        else:
            return float(value - self.getMinNegativePwm()) / self.getFullRangeScaleFactor()

    def setSpeed(self, speed):
        """Set the PWM value based on a speed.

        This is intended to be used by speed controllers.

        .. note::

            :func:`setBounds` must be called first.

        :param speed: The speed to set the speed controller between -1.0 and
            1.0.
        :type speed: float
        """
        # clamp speed to be in the range 1.0 >= speed >= -1.0
        if speed < -1.0:
            speed = -1.0
        elif speed > 1.0:
            speed = 1.0

        # calculate the desired output pwm value by scaling the speed
        # appropriately
        if speed == 0.0:
            rawValue = self.getCenterPwm()
        elif speed > 0.0:
            rawValue = int(speed * self.getPositiveScaleFactor() +
                           self.getMinPositivePwm() + 0.5)
        else:
            rawValue = int(speed * self.getNegativeScaleFactor() +
                           self.getMaxNegativePwm() + 0.5)

        # send the computed pwm value to the FPGA
        self.setRaw(rawValue)

    def getSpeed(self):
        """Get the PWM value in terms of speed.

        This is intended to be used by speed controllers.

        .. note::

            :func:`setBounds` must be called first.

        :returns: The most recently set speed between -1.0 and 1.0.
        :rtype: float
        """
        value = self.getRaw()
        if value > self.getMaxPositivePwm():
            return 1.0
        elif value < self.getMinNegativePwm():
            return -1.0
        elif value > self.getMinPositivePwm():
            return float(value - self.getMinPositivePwm()) / self.getPositiveScaleFactor()
        elif value < self.getMaxNegativePwm():
            return float(value - self.getMaxNegativePwm()) / self.getNegativeScaleFactor()
        else:
            return 0.0

    def setRaw(self, value):
        """Set the PWM value directly to the hardware.

        Write a raw value to a PWM channel.

        :param value: Raw PWM value.  Range 0 - 255.
        :type value: int
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.setPWM(self.port, value)

    def getRaw(self):
        """Get the PWM value directly from the hardware.

        Read a raw value from a PWM channel.

        :returns: Raw PWM control value.  Range: 0 - 255.
        :rtype: int
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        return hal.getPWM(self.port)

    def setPeriodMultiplier(self, mult):
        """Slow down the PWM signal for old devices.

        :param mult: The period multiplier to apply to this channel
        :type mult: PWM.PeriodMultiplier
        """
        if self.port is None:
            raise ValueError("operation on freed port")
        if mult == PWM.PeriodMultiplier.k4X:
            # Squelch 3 out of 4 outputs
            hal.setPWMPeriodScale(self.port, 3)
        elif mult == PWM.PeriodMultiplier.k2X:
            # Squelch 1 out of 2 outputs
            hal.setPWMPeriodScale(self.port, 1)
        elif mult == PWM.PeriodMultiplier.k1X:
            # Don't squelch any outputs
            hal.setPWMPeriodScale(self.port, 0)
        else:
            raise ValueError("Invalid mult argument '%s'" % mult)

    def setZeroLatch(self):
        if self.port is None:
            raise ValueError("operation on freed port")
        hal.latchPWMZero(self.port)

    def getMaxPositivePwm(self):
        return self.maxPwm

    def getMinPositivePwm(self):
        if self.eliminateDeadband:
            return self.deadbandMaxPwm
        else:
            return self.centerPwm + 1

    def getCenterPwm(self):
        return self.centerPwm

    def getMaxNegativePwm(self):
        if self.eliminateDeadband:
            return self.deadbandMinPwm
        else:
            return self.centerPwm - 1

    def getMinNegativePwm(self):
        return self.minPwm

    def getPositiveScaleFactor(self):
        """Get the scale for positive speeds."""
        return self.getMaxPositivePwm() - self.getMinPositivePwm()

    def getNegativeScaleFactor(self):
        """Get the scale for negative speeds."""
        return self.getMaxNegativePwm() - self.getMinNegativePwm()

    def getFullRangeScaleFactor(self):
        """Get the scale for positions."""
        return self.getMaxPositivePwm() - self.getMinNegativePwm()

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Speed Controller"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.getSpeed())

    def valueChanged(self, itable, key, value, bln):
        self.setSpeed(float(value))

    def startLiveWindowMode(self):
        self.setSpeed(0) # Stop for safety
        super().startLiveWindowMode()

    def stopLiveWindowMode(self):
        super().stopLiveWindowMode()
        self.setSpeed(0) # Stop for safety
