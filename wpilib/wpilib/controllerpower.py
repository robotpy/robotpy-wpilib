# validated: 2015-12-24 DS 6d854af athena/java/edu/wpi/first/wpilibj/ControllerPower.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

__all__ = ['ControllerPower']

class ControllerPower:
    """Provides access to power levels on the roboRIO"""

    @staticmethod
    def getInputVoltage():
        """
            Get the input voltage to the robot controller
            
            :returns: The controller input voltage value in Volts
            :rtype: float
        """
        return hal.getVinVoltage()
    
    @staticmethod
    def getInputCurrent():
        """
            Get the input current to the robot controller
            
            :returns: The controller input current value in Amps
            :rtype: float
        """
        return hal.getVinCurrent()
    
    @staticmethod
    def getVoltage3V3():
        """
            Get the voltage of the 3.3V rail
            
            :returns: The controller 3.3V rail voltage value in Volts
            :rtype: float
        """
        return hal.getUserVoltage3V3()
    
    @staticmethod
    def getCurrent3V3():
        """
            Get the current output of the 3.3V rail
            
            :returns: The controller 3.3V rail output current value in Amps
            :rtype: float
        """
        return hal.getUserCurrent3V3()
    
    @staticmethod
    def getEnabled3V3():
        """
            Get the enabled state of the 3.3V rail. The rail may be
            disabled due to a controller brownout, a short circuit on the
            rail, or controller over-voltage
            
            :returns: True if enabled, False otherwise
            :rtype: bool
        """
        return hal.getUserActive3V3();
    
    @staticmethod
    def getFaultCount3V3():
        """
            Get the count of the total current faults on the 3.3V rail since
            the controller has booted
            
            :returns: The number of faults
            :rtype: int
        """
        return hal.getUserCurrentFaults3V3()
    
    @staticmethod
    def getVoltage5V():
        """
            Get the voltage of the 5V rail
            
            :returns: The controller 5V rail voltage value in Volts
            :rtype: float
        """
        return hal.getUserVoltage5V()
    
    @staticmethod
    def getCurrent5V():
        """
            Get the current output of the 5V rail
            
            :returns: The controller 5V rail output current value in Amps
            :rtype: float
        """
        return hal.getUserCurrent5V()
    
    @staticmethod
    def getEnabled5V():
        """
            Get the enabled state of the 5V rail. The rail may be disabled
            due to a controller brownout, a short circuit on the rail, or
            controller over-voltage
            
            :returns: True if enabled, False otherwise
            :rtype: bool
        """
        return hal.getUserActive5V()
    
    @staticmethod
    def getFaultCount5V():
        """
            Get the count of the total current faults on the 5V rail since
            the controller has booted
            
            :returns: The number of faults
            :rtype: int
        """
        return hal.getUserCurrentFaults5V()
    
    @staticmethod
    def getVoltage6V():
        """
            Get the voltage of the 6V rail
            
            :returns: The controller 6V rail voltage value in Volts
            :rtype: float
        """
        return hal.getUserVoltage6V()
    
    @staticmethod
    def getCurrent6V():
        """
            Get the current output of the 6V rail
            
            :returns: The controller 6V rail output current value in Amps
            :rtype: float
        """
        return hal.getUserCurrent6V()
    
    @staticmethod
    def getEnabled6V():
        """
            Get the enabled state of the 6V rail. The rail may be disabled
            due to a controller brownout, a short circuit on the rail, or
            controller over-voltage
            
            :returns: True if enabled, False otherwise
            :rtype: bool
        """
        return hal.getUserActive6V()
    
    @staticmethod
    def getFaultCount6V():
        """
            Get the count of the total current faults on the 6V rail since
            the controller has booted
            
            :returns: The number of faults
            :rtype: int
        """
        return hal.getUserCurrentFaults6V()

