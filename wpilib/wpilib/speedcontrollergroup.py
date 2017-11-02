# validated: 2017-10-23 TW 877a9eae1fcc edu/wpi/first/wpilibj/SpeedControllerGroup.java

# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .interfaces.speedcontroller import SpeedController

__all__ = ["SpeedControllerGroup"]


class SpeedControllerGroup(SpeedController):
    def __init__(self, *args):
        self.speedControllers = args
        self.isInverted = False

    def set(self, speed):
        for speedController in self.speedControllers:
            speedController.set(-speed if self.isInverted else speed)

    def get(self):
        if len(self.speedControllers) > 0:
            return self.speedControllers[0].get()
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
        for speedController in self.speedControllers:
            speedController.pidWrite(output)
