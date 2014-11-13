#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

__all__ = ['ControllerPower']

class ControllerPower:

    @staticmethod
    def getInputVoltage():
        return hal.getVinVoltage()
    
    @staticmethod
    def getInputCurrent():
        return hal.getVinCurrent()
    
    @staticmethod
    def getVoltage3V3():
        return hal.getUserVoltage3V3()
    
    @staticmethod
    def getCurrent3V3():
        return hal.getUserCurrent3V3()
    
    @staticmethod
    def getEnabled3V3():
        return hal.getUserActive3V3();
    
    @staticmethod
    def getFaultCount3V3():
        return hal.getUserCurrentFaults3V3()
    
    @staticmethod
    def getVoltage5V():
        return hal.getUserVoltage5V()
    
    @staticmethod
    def getCurrent5V():
        return hal.getUserCurrent5V()
    
    @staticmethod
    def getEnabled5V():
        return hal.getUserActive5V()
    
    @staticmethod
    def getFaultCount5V():
        return hal.getUserCurrentFaults5V()
    
    @staticmethod
    def getVoltage6V():
        return hal.getUserVoltage6V()
    
    @staticmethod
    def getCurrent6V():
        return hal.getUserCurrent6V()
    
    @staticmethod
    def getEnabled6V():
        return hal.getUserActive6V()
    
    @staticmethod
    def getFaultCount6V():
        return hal.getUserCurrentFaults6V()

