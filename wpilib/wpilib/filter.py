# validated: 2016-01-08 DS e15ca5a shared/java/edu/wpi/first/wpilibj/filters/Filter.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2015-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .interfaces.pidsource import PIDSource

__all__ = ['Filter']

class Filter:
    """Superclass for filters"""
    
    def __init__(self, source):
        """Constructor.
        
        :param source:
        :type source: :class:`.PIDSource`, callable
        """
        self.source = PIDSource.from_obj_or_callable(source)
        
    def setPIDSourceType(self, pidSourceType):
        self.source.setPIDSourceType(pidSourceType)
        
    def getPIDSourceType(self):
        return self.source.getPIDSourceType()
    
    def pidGet(self):
        raise NotImplementedError
    
    def get(self):
        """Returns the current filter estimate without also inserting new data as
        :meth:`pidGet` would do.
        
        :returns: The current filter estimate
        """
        raise NotImplementedError
    
    def reset(self):
        """Reset the filter state"""
        raise NotImplementedError
    
    def pidGetSource(self):
        """Calls PIDGet() of source
        
        :returns: Current value of source
        """
        return self.source.pidGet()
        