#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .pidoutput import PIDOutput

__all__ = ["SpeedController"]

class SpeedController(PIDOutput):
    """Interface for speed controlling devices."""

    def get(self):
        """Common interface for getting the current set speed of a speed
        controller.

        :returns: The current set speed.  Value is between -1.0 and 1.0.
        """
        raise NotImplementedError

    def set(self, speed, syncGroup=0):
        """Common interface for setting the speed of a speed controller.

        :param speed: The speed to set.  Value should be between -1.0 and 1.0.
        :param syncGroup: The update group to add this set() to, pending
                          updateSyncGroup().  If 0 (or unspecified), update
                          immediately.
        """
        raise NotImplementedError

    def disable(self):
        """Disable the speed controller."""
        raise NotImplementedError
