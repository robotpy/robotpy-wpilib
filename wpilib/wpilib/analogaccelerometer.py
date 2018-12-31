# validated: 2018-09-09 EN ecfe95383cdf edu/wpi/first/wpilibj/AnalogAccelerometer.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Union

import hal

from .analoginput import AnalogInput
from .interfaces import PIDSource
from .sendablebase import SendableBase
from .sendablebuilder import SendableBuilder

__all__ = ["AnalogAccelerometer"]


class AnalogAccelerometer(SendableBase):
    """Analog Accelerometer
    
    The accelerometer reads acceleration directly through the sensor. Many
    sensors have multiple axis and can be treated as multiple devices. Each
    is calibrated by finding the center value over a period of time.
    
    .. not_implemented: initAccelerometer
    """

    PIDSourceType = PIDSource.PIDSourceType

    def __init__(self, channel: Union[AnalogInput, int]) -> None:
        """Constructor. Create a new instance of Accelerometer from either an existing
        AnalogChannel or from an analog channel port index.

        :param channel: port index or an already initialized AnalogInput
        """
        super().__init__()
        if not hasattr(channel, "getAverageVoltage"):  # If 'channel' is an integer
            self.analogChannel = AnalogInput(channel)
            self.allocatedChannel = True
            self.addChild(self.analogChannel)
        else:
            self.allocatedChannel = False
            self.analogChannel = channel
        self.voltsPerG = 1.0
        self.zeroGVoltage = 2.5
        self.pidSource = self.PIDSourceType.kDisplacement
        hal.report(
            hal.UsageReporting.kResourceType_Accelerometer,
            self.analogChannel.getChannel(),
        )
        self.setName("Accelerometer", self.analogChannel.getChannel())

    def close(self) -> None:
        super().close()
        if self.analogChannel and self.allocatedChannel:
            self.analogChannel.close()
        self.analogChannel = None

    def getAcceleration(self) -> float:
        """Return the acceleration in Gs.

        The acceleration is returned units of Gs.

        :returns: The current acceleration of the sensor in Gs.
        """
        if not self.analogChannel:
            return 0.0
        return (
            self.analogChannel.getAverageVoltage() - self.zeroGVoltage
        ) / self.voltsPerG

    def setSensitivity(self, sensitivity: float) -> None:
        """Set the accelerometer sensitivity.

        This sets the sensitivity of the accelerometer used for calculating
        the acceleration.  The sensitivity varies by accelerometer model.
        There are constants defined for various models.

        :param sensitivity: The sensitivity of accelerometer in Volts per G.
        """
        self.voltsPerG = sensitivity

    def setZero(self, zero: float) -> None:
        """Set the voltage that corresponds to 0 G.

        The zero G voltage varies by accelerometer model. There are constants
        defined for various models.

        :param zero: The zero G voltage.
        """
        self.zeroGVoltage = zero

    def setPIDSourceType(self, pidSource: PIDSourceType) -> None:
        """Set which parameter you are using as a process
        control variable. 

        :param pidSource: An enum to select the parameter.
        """
        self.pidSource = pidSource

    def getPIDSourceType(self) -> PIDSourceType:
        return self.pidSource

    def pidGet(self) -> float:
        """Get the Acceleration for the PID Source parent.

        :returns: The current acceleration in Gs.
        """
        return self.getAcceleration()

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setSmartDashboardType("Accelerometer")
        builder.addDoubleProperty("Value", self.getAcceleration, None)
