# validated: 2017-12-27 TW f9bece2ffbf7 edu/wpi/first/wpilibj/AnalogAccelerometer.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .analoginput import AnalogInput
from .interfaces import PIDSource
from .sensorbase import SensorBase

__all__ = ["AnalogAccelerometer"]

class AnalogAccelerometer(SensorBase):
    """Analog Accelerometer
    
    The accelerometer reads acceleration directly through the sensor. Many
    sensors have multiple axis and can be treated as multiple devices. Each
    is calibrated by finding the center value over a period of time.
    
    .. not_implemented: initAccelerometer
    """
    
    PIDSourceType = PIDSource.PIDSourceType

    def __init__(self, channel):
        """Constructor. Create a new instance of Accelerometer from either an existing
        AnalogChannel or from an analog channel port index.

        :param channel: port index or an already initialized AnalogInput
        :type channel: int or :class:`.AnalogInput`
        """
        super().__init__()
        if not hasattr(channel, "getAverageVoltage"): # If 'channel' is an integer
            self.analogChannel = AnalogInput(channel)
            self.allocatedChannel = True
            self.addChild(self.analogChannel)
        else:
            self.allocatedChannel = False
            self.analogChannel = channel
        self.voltsPerG = 1.0
        self.zeroGVoltage = 2.5
        self.pidSource = self.PIDSourceType.kDisplacement
        hal.report(hal.UsageReporting.kResourceType_Accelerometer,
                      self.analogChannel.getChannel())
        self.setName("Accelerometer", self.analogChannel.getChannel())

    def free(self):
        super().free()
        if self.analogChannel and self.allocatedChannel:
            self.analogChannel.free()
        self.analogChannel = None


    def getAcceleration(self):
        """Return the acceleration in Gs.

        The acceleration is returned units of Gs.

        :returns: The current acceleration of the sensor in Gs.
        :rtype: float
        """
        if not self.analogChannel:
            return 0.0
        return (self.analogChannel.getAverageVoltage() - self.zeroGVoltage) / self.voltsPerG

    def setSensitivity(self, sensitivity):
        """Set the accelerometer sensitivity.

        This sets the sensitivity of the accelerometer used for calculating
        the acceleration.  The sensitivity varies by accelerometer model.
        There are constants defined for various models.

        :param sensitivity: The sensitivity of accelerometer in Volts per G.
        :type  sensitivity: float
        """
        self.voltsPerG = sensitivity

    def setZero(self, zero):
        """Set the voltage that corresponds to 0 G.

        The zero G voltage varies by accelerometer model. There are constants
        defined for various models.

        :param zero: The zero G voltage.
        :type  zero: float
        """
        self.zeroGVoltage = zero
        
    def setPIDSourceType(self, pidSource):
        """Set which parameter you are using as a process
        control variable. 

        :param pidSource: An enum to select the parameter.
        :type  pidSource: :class:`.PIDSource.PIDSourceType`
        """
        self.pidSource = pidSource
        
    def getPIDSourceType(self):
        return self.pidSource

    def pidGet(self):
        """Get the Acceleration for the PID Source parent.

        :returns: The current acceleration in Gs.
        :rtype: float
        """
        return self.getAcceleration()

    def initSendable(self, builder):
        builder.setSmartDashboardType("Accelerometer")
        builder.addDoubleProperty("Value", self.getAcceleration, None)
