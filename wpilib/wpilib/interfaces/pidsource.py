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
    
    @staticmethod
    def from_obj_or_callable(objc):
        """
            Utility method that gets a PIDSource object
        
            :param objc: An object that implements the PIDSource interface, or
                         a callable
                         
            :returns: an object that implements the PIDSource interface 
        """
        
        # This isn't pythonic, but will cause errors to happen earlier
        if not hasattr(objc, 'pidGet'):
            if not callable(objc):
                raise TypeError("%s must be callable or ")
            return _PIDSourceWrapper(objc)
        
        if not hasattr(objc, 'getPIDSourceType'):
            raise TypeError("%s does not have getPIDSourceType method" % objc)
            
        return objc
    
        
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

class _PIDSourceWrapper(PIDSource):
    
    def __init__(self, fn):
        self.pidGet = fn
    
    def getPIDSourceType(self):
        return self.PIDSourceType.kDisplacement
