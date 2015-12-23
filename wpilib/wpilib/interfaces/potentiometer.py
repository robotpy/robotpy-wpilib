# validated: 2015-12-22 DS 6d854af shared/java/edu/wpi/first/wpilibj/interfaces/Potentiometer.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .pidsource import PIDSource

__all__ = ["Potentiometer"]

class Potentiometer(PIDSource):
    def get(self):
        raise NotImplementedError
