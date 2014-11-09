#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

__all__ = ["PIDSource"]

class PIDSource:
    """This interface allows for :class:`.PIDController` to automatically read from this
    object.
    """

    class PIDSourceParameter:
        """A description for the type of output value to provide to a
        :class:`.PIDController`"""
        kDistance = 0
        kRate = 1
        kAngle = 2

    def pidGet(self):
        """Get the result to use in :class:`.PIDController`
        
        :returns: the result to use in PIDController
        """
        raise NotImplementedError
