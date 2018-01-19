# validated: 2018-01-19 DS 0e8ff4663df9 edu/wpi/first/wpilibj/SpeedControllerGroup.java

# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .interfaces.speedcontroller import SpeedController
from .sendablebase import SendableBase

__all__ = ["SpeedControllerGroup"]


class SpeedControllerGroup(SendableBase, SpeedController):
    """Allows multiple :class:`.SpeedController` objects to be linked together."""

    instances = 0

    def __init__(self, speedController, *args):
        """Create a new SpeedControllerGroup with the provided SpeedControllers.

        :param args: SpeedControllers to add
        :type args: :class:`.SpeedController`
        """
        SendableBase.__init__(self)
        SpeedController.__init__(self)

        self.speedControllers = [speedController] + list(args)

        for speedcontroller in self.speedControllers:
            self.addChild(speedcontroller)

        self.isInverted = False

        SpeedControllerGroup.instances += 1
        self.setName("SpeedControllerGroup", self.instances)

    def set(self, speed):
        for speedController in self.speedControllers:
            speedController.set(-speed if self.isInverted else speed)

    def get(self):
        if len(self.speedControllers) > 0:
            return self.speedControllers[0].get() * (-1 if self.isInverted else 1)
        return 0.0

    def setInverted(self, isInverted):
        self.isInverted = isInverted

    def getInverted(self):
        return self.isInverted

    def stopMotor(self):
        for speedController in self.speedControllers:
            speedController.stopMotor()

    def disable(self):
        for speedController in self.speedControllers:
            speedController.disable()

    def pidWrite(self, output):
        self.set(output)

    def initSendable(self, builder):
        builder.setSmartDashboardType("Speed Controller")
        builder.setSafeState(self.stopMotor)
        builder.addDoubleProperty("Value", self.get, self.set)
