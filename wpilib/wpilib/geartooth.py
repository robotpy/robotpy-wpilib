# validated: 2017-12-26 EN f9bece2ffbf7 edu/wpi/first/wpilibj/GearTooth.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

from .counter import Counter
from .livewindow import LiveWindow
from .sendablebuilder import SendableBuilder

__all__ = ["GearTooth"]


class GearTooth(Counter):
    """Interface to the gear tooth sensor supplied by FIRST
    
    Currently there is no reverse sensing on the gear tooth sensor, but in
    future versions we might implement the necessary timing in the FPGA to
    sense direction.
    """

    kGearToothThreshold = 55e-6

    def enableDirectionSensing(self, directionSensitive: bool) -> None:
        if directionSensitive:
            self.setPulseLengthMode(GearTooth.kGearToothThreshold)

    def __init__(self, channel: int, directionSensitive: bool = False) -> None:
        """Construct a GearTooth sensor.

        :param channel: The DIO channel index or DigitalSource that the sensor
            is connected to.
        :param directionSensitive: True to enable the pulse length decoding in
            hardware to specify count direction.  Defaults to False.
        """
        super().__init__(channel)
        self.enableDirectionSensing(directionSensitive)
        if hasattr(self.upSource, "getChannel"):
            if directionSensitive:
                hal.report(
                    hal.UsageReporting.kResourceType_GearTooth,
                    self.upSource.getChannel(),
                    0,
                    "D",
                )
            else:
                hal.report(
                    hal.UsageReporting.kResourceType_GearTooth,
                    self.upSource.getChannel(),
                    0,
                )
        self.setName("GearTooth", self.upSource.getChannel())

    def initSendable(self, builder: SendableBuilder) -> None:
        super().initSendable(builder)
        builder.setSmartDashboardType("Gear Tooth")
