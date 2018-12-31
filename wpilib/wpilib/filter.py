# validated: 2017-11-21 EN e1195e8b9dab edu/wpi/first/wpilibj/filters/Filter.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2015-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .interfaces.pidsource import PIDSource

__all__ = ["Filter"]


class Filter:
    """Superclass for filters"""

    def __init__(self, source: PIDSource) -> None:
        """Constructor.
        
        :param source:
        """
        self.source = PIDSource.from_obj_or_callable(source)

    def setPIDSourceType(self, pidSourceType: PIDSource.PIDSourceType) -> None:
        self.source.setPIDSourceType(pidSourceType)

    def getPIDSourceType(self) -> PIDSource.PIDSourceType:
        return self.source.getPIDSourceType()

    def pidGet(self) -> float:
        raise NotImplementedError

    def get(self) -> float:
        """Returns the current filter estimate without also inserting new data as
        :meth:`pidGet` would do.
        
        :returns: The current filter estimate
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Reset the filter state"""
        raise NotImplementedError

    def pidGetSource(self) -> float:
        """Calls PIDGet() of source
        
        :returns: Current value of source
        """
        return self.source.pidGet()
