# validated: 2016-12-22 JW 69422dc0636c athena/java/edu/wpi/first/wpilibj/AnalogGyro.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .analoginput import AnalogInput
from .gyrobase import GyroBase
from .interfaces import PIDSource
from .livewindow import LiveWindow
from .timer import Timer

__all__ = ["AnalogGyro"]

class AnalogGyro(GyroBase):
    """Interface to a gyro device via an :class:`.AnalogInput`
    
    Use a rate gyro to return the robots heading relative to a starting
    position.  The Gyro class tracks the robots heading based on the starting
    position. As the robot rotates the new heading is computed by integrating
    the rate of rotation returned by the sensor. When the class is
    instantiated, it does a short calibration routine where it samples the
    gyro while at rest to determine the default offset. This is subtracted
    from each sample to determine the heading.

    .. not_implemented: initGyro
    """

    kOversampleBits = 10
    kAverageBits = 0
    kSamplesPerSecond = 50.0
    kCalibrationSampleTime = 5.0
    kDefaultVoltsPerDegreePerSecond = 0.007
    
    PIDSourceType = PIDSource.PIDSourceType
    
    def __init__(self, channel, center=None, offset=None):
        """Gyro constructor.

        Also initializes the gyro. Calibrate the gyro by running for a number
        of samples and computing the center value. Then use the
        center value as the Accumulator center value for subsequent
        measurements. It's important to make sure that the robot is not
        moving while the centering calculations are in progress, this is
        typically done when the robot is first turned on while it's sitting
        at rest before the competition starts.

        :param channel: The analog channel index or AnalogInput object that
            the gyro is connected to. Gyros can only be used on on-board channels 0-1.
        :param center: Preset uncalibrated value to use as the accumulator center value
        :type center: int
        :param offset: Preset uncalibrated value to use as the gyro offset
        :type offset: float
        """
        
        if not hasattr(channel, "initAccumulator"):
            channel = AnalogInput(channel)
            self.channelAllocated = True
        else:
            self.channelAllocated = False
            
        self.analog = channel

        self.gyroHandle = hal.initializeAnalogGyro(self.analog.port)
    
           
        self.setDeadband(0.0)

        hal.setupAnalogGyro(self.gyroHandle)
        
        hal.report(hal.UsageReporting.kResourceType_Gyro,
                      self.analog.getChannel())
        LiveWindow.addSensorChannel("AnalogGyro", self.analog.getChannel(), self)
        
        if center is None or offset is None:
            self.calibrate()
        else:
            hal.setAnalogGyroParameters(self.gyroHandle, self.kDefaultVoltsPerDegreePerSecond, offset, center)        
            self.reset()
        
        
    def calibrate(self):
        """:see: :meth:`.Gyro.calibrate`"""
        hal.calibrateAnalogGyro(self.gyroHandle)
        
    def reset(self):
        """:see: :meth:`.Gyro.reset`"""
        hal.resetAnalogGyro(self.gyroHandle)

    def free(self):
        """:see: :meth:`.Gyro.free`"""
        LiveWindow.removeComponent(self)
        if self.analog is not None and self.channelAllocated:
            self.analog.free()
            self.analog = None
        hal.freeAnalogGyro(self.gyroHandle)
        self.gyroHandle = 0
        
    def getAngle(self):
        """:see: :meth:`.Gyro.getAngle`"""
    
        if self.analog is None:
            return 0.0
        
        return hal.getAnalogGyroAngle(self.gyroHandle)

    def getRate(self):
        """:see: :meth:`.Gyro.getRate`"""
        if self.analog is None:
            return 0.0
        else:
            return hal.getAnalogGyroRate(self.gyroHandle)

    def getOffset(self):
        """Return the gyro offset value set during calibration to
        use as a future preset
        
        :returns: the current offset value
        """
        return hal.getAnalogGyroOffset(self.gyroHandle)
    
    def getCenter(self):
        """Return the gyro center value set during calibration to
        use as a future preset
        
        :returns: the current center value
        """
        return hal.getAnalogGyroCenter(self.gyroHandle)

    def setSensitivity(self, voltsPerDegreePerSecond):
        """Set the gyro sensitivity. This takes the number of
        volts/degree/second sensitivity of the gyro and uses it in subsequent
        calculations to allow the code to work with multiple gyros. This value
        is typically found in the gyro datasheet.

        :param voltsPerDegreePerSecond:
            The sensitivity in Volts/degree/second
        :type  voltsPerDegreePerSecond: float
        """
        hal.setAnalogGyroVoltsPerDegreePerSecond(self.gyroHandle, voltsPerDegreePerSecond)

    def setDeadband(self, volts):
        """Set the size of the neutral zone.  Any voltage from the gyro less
        than this amount from the center is considered stationary.  Setting a
        deadband will decrease the amount of drift when the gyro isn't
        rotating, but will make it less accurate.

        :param volts: The size of the deadband in volts
        :type  volts: float
        """
        if self.analog is None:
            return
        
        hal.setAnalogGyroDeadband(self.gyroHandle, volts)

