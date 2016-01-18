#----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .controller import Controller

__all__ = ['PIDInterface']

class PIDInterface(Controller):
    
    def setPID(self, p, i, d):
        raise NotImplementedError
    
    def getP(self):
        raise NotImplementedError
    
    def getI(self):
        raise NotImplementedError
    
    def getD(self):
        raise NotImplementedError
    
    def setSetpoint(self, setpoint):
        raise NotImplementedError
    
    def getSetpoint(self):
        raise NotImplementedError
    
    def getError(self):
        raise NotImplementedError
    
    def enable(self):
        raise NotImplementedError
        
    def disable(self):
        raise NotImplementedError
        
    def isEnabled(self):
        raise NotImplementedError
        
    def reset(self):
        raise NotImplementedError
