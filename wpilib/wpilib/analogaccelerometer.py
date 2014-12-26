#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .analoginput import AnalogInput
from .livewindow import LiveWindow
from .livewindowsendable import LiveWindowSendable

__all__ = ["AnalogAccelerometer"]

class AnalogAccelerometer(LiveWindowSendable):
    """Analog Accelerometer
    
    The accelerometer reads acceleration directly through the sensor. Many
    sensors have multiple axis and can be treated as multiple devices. Each
    is calibrated by finding the center value over a period of time.
    
    .. not_implemented: initAccelerometer
    """

    def __init__(self, channel):
        """Create a new instance of Accelerometer from either an existing
        AnalogChannel or from an analog channel port index.

        :param channel: port index or an already initialized :class:`.AnalogInput`
        """
        if not hasattr(channel, "getAverageVoltage"):
            channel = AnalogInput(channel)
        self.analogChannel = channel
        self.voltsPerG = 1.0
        self.zeroGVoltage = 2.5
        hal.HALReport(hal.HALUsageReporting.kResourceType_Accelerometer,
                      self.analogChannel.getChannel())
        LiveWindow.addSensorChannel("Accelerometer",
                                    self.analogChannel.getChannel(), self)

    def getAcceleration(self):
        """Return the acceleration in Gs.

        The acceleration is returned units of Gs.

        :returns: The current acceleration of the sensor in Gs.
        :rtype: float
        """
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

    def pidGet(self):
        """Get the Acceleration for the PID Source parent.

        :returns: The current acceleration in Gs.
        :rtype: float
        """
        return self.getAcceleration()

    def getSmartDashboardType(self):
        return "Accelerometer"

    # Live Window code, only does anything if live window is activated.

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.getAcceleration())

    def startLiveWindowMode(self):
        # Don't have to do anything special when entering the LiveWindow.
        pass

    def stopLiveWindowMode(self):
        # Don't have to do anything special when exiting the LiveWindow.
        pass
