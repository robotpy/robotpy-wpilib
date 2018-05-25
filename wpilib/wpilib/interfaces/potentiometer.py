# validated: 2017-09-27 AA e1195e8b9dab edu/wpi/first/wpilibj/interfaces/Potentiometer.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .pidsource import PIDSource

__all__ = ["Potentiometer"]


class Potentiometer(PIDSource):
    """Interface for a Potentiometer."""

    def get(self) -> float:
        raise NotImplementedError
