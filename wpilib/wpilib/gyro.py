#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .analoginput import AnalogInput
from .interfaces import PIDSource
from .livewindow import LiveWindow
from .sensorbase import SensorBase
from .timer import Timer

__all__ = ["Gyro"]

class Gyro(SensorBase):
    """Use a rate gyro to return the robots heading relative to a starting
    position.  The Gyro class tracks the robots heading based on the starting
    position. As the robot rotates the new heading is computed by integrating
    the rate of rotation returned by the sensor. When the class is
    instantiated, it does a short calibration routine where it samples the
    gyro while at rest to determine the default offset. This is subtracted
    from each sample to determine the heading.
    """

    kOversampleBits = 10
    kAverageBits = 0
    kSamplesPerSecond = 50.0
    kCalibrationSampleTime = 5.0
    kDefaultVoltsPerDegreePerSecond = 0.007

    def __init__(self, channel):
        """Gyro constructor.

        Also initializes the gyro. Calibrate the gyro by running for a number
        of samples and computing the center value for this part. Then use the
        center value as the Accumulator center value for subsequent
        measurements. It's important to make sure that the robot is not
        moving while the centering calculations are in progress, this is
        typically done when the robot is first turned on while it's sitting
        at rest before the competition starts.

        :param channel: The analog channel index or AnalogChannel object that
            the gyro is connected to.
        """
        if not hasattr(channel, "initAccumulator"):
            channel = AnalogInput(channel)
        self.analog = channel

        self.voltsPerDegreePerSecond = Gyro.kDefaultVoltsPerDegreePerSecond
        self.analog.setAverageBits(Gyro.kAverageBits)
        self.analog.setOversampleBits(Gyro.kOversampleBits)
        sampleRate = Gyro.kSamplesPerSecond \
                * (1 << (Gyro.kAverageBits + Gyro.kOversampleBits))
        AnalogInput.setGlobalSampleRate(sampleRate)
        Timer.delay(1.0)

        self.analog.initAccumulator()
        self.analog.resetAccumulator()

        Timer.delay(Gyro.kCalibrationSampleTime)

        value, count = self.analog.getAccumulatorOutput()

        self.center = int(float(value) / float(count) + .5)

        self.offset = (float(value) / float(count)) - self.center

        self.analog.setAccumulatorCenter(self.center)
        self.analog.resetAccumulator()

        self.setDeadband(0.0)

        self.pidSource = PIDSource.PIDSourceParameter.kAngle

        hal.HALReport(hal.HALUsageReporting.kResourceType_Gyro,
                      self.analog.getChannel())
        LiveWindow.addSensorChannel("Gyro", self.analog.getChannel(), self)

    def reset(self):
        """Reset the gyro. Resets the gyro to a heading of zero. This can be
        used if there is significant drift in the gyro and it needs to be
        recalibrated after it has been running.
        """
        if self.analog is None:
            return
        self.analog.resetAccumulator()

    def free(self):
        """Delete (free) the accumulator and the analog components used for the
        gyro.
        """
        if self.analog is not None:
            self.analog.free()
            self.analog = None

    def getAngle(self):
        """Return the actual angle in degrees that the robot is currently
        facing.

        The angle is based on the current accumulator value corrected by the
        oversampling rate, the gyro type and the A/D calibration values. The
        angle is continuous, that is can go beyond 360 degrees. This make
        algorithms that wouldn't want to see a discontinuity in the gyro output
        as it sweeps past 0 on the second time around.

        :returns: The current heading of the robot in degrees. This heading is
                based on integration of the returned rate from the gyro.
        """
        if self.analog is None:
            return 0.0
        value, count = self.analog.getAccumulatorOutput()

        value -= count * self.offset

        return (value
                * 1e-9
                * self.analog.getLSBWeight()
                * (1 << self.analog.getAverageBits())
                / (AnalogInput.getGlobalSampleRate() * self.voltsPerDegreePerSecond))

    def getRate(self):
        """Return the rate of rotation of the gyro

        The rate is based on the most recent reading of the gyro analog value

        :returns: the current rate in degrees per second
        """
        if self.analog is None:
            return 0.0
        else:
            return ((self.analog.getAverageValue() - (self.center + self.offset))
                    * 1e-9
                    * self.analog.getLSBWeight()
                    / ((1 << self.analog.getOversampleBits()) * self.voltsPerDegreePerSecond))

    def setSensitivity(self, voltsPerDegreePerSecond):
        """Set the gyro type based on the sensitivity. This takes the number of
        volts/degree/second sensitivity of the gyro and uses it in subsequent
        calculations to allow the code to work with multiple gyros.

        :param voltsPerDegreePerSecond:
            The type of gyro specified as the voltage that represents one
            degree/second.
        """
        self.voltsPerDegreePerSecond = voltsPerDegreePerSecond

    def setDeadband(self, volts):
        """Set the size of the neutral zone.  Any voltage from the gyro less
        than this amount from the center is considered stationary.  Setting a
        deadband will decrease the amount of drift when the gyro isn't
        rotating, but will make it less accurate.

        :param volts: The size of the deadband in volts
        """
        if self.analog is None:
            return
        deadband = int(volts * 1e9 / self.analog.getLSBWeight() *
                       (1 << self.analog.getOversampleBits()))
        self.analog.setAccumulatorDeadband(deadband)

    def setPIDSourceParameter(self, pidSource):
        """Set which parameter of the encoder you are using as a process
        control variable. The Gyro class supports the rate and angle
        parameters.

        :param pidSource: An enum to select the parameter.
        """
        if pidSource not in (1, 2):
            raise ValueError("Must be kRate or kAngle")
        self.pidSource = pidSource

    def pidGet(self):
        """Get the angle of the gyro for use with PIDControllers

        :returns: the current angle according to the gyro
        """
        if self.pidSource == PIDSource.PIDSourceParameter.kRate:
            return self.getRate()
        elif self.pidSource == PIDSource.PIDSourceParameter.kAngle:
            return self.getAngle()
        else:
            return 0.0

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Gyro"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.getAngle())

    def startLiveWindowMode(self):
        pass

    def stopLiveWindowMode(self):
        pass
