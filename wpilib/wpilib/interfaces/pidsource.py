# validated: 2015-12-22 DS 6d854af shared/java/edu/wpi/first/wpilibj/PIDSource.java
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

    class PIDSourceType:
        """A description for the type of output value to provide to a
        :class:`.PIDController`"""
        kDisplacement = 0
        kRate = 1
        
    def setPIDSourceType(self, pidSource):
        """Set which parameter of the device you are using as a process control
        variable.
        
        :param pidSource: An enum to select the parameter.
        :type pidSource: :class:`.PIDSourceType`
        """
        raise NotImplementedError
        
    def getPIDSourceType(self):
        """Get which parameter of the device you are using as a process control
           variable.
           
        :returns: the currently selected PID source parameter
        """
        raise NotImplementedError

    def pidGet(self):
        """Get the result to use in :class:`.PIDController`
        
        :returns: the result to use in PIDController
        """
        raise NotImplementedError
