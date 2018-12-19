# validated: 2018-01-19 DS 02b6615042d8 edu/wpi/first/wpilibj/RobotController.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Tuple

import hal

__all__ = ["RobotController"]


class RobotController:
    """
        Contains functions for roboRIO functionality.
    """

    @staticmethod
    def getFPGAVersion() -> int:
        """Return the FPGA Version number. For now, expect this to be the current
        year.
        
        :returns: FPGA Version number.
        """
        return hal.getFPGAVersion()

    @staticmethod
    def getFPGARevision() -> int:
        """Return the FPGA Revision number. The format of the revision is 3 numbers. The 12 most
        significant bits are the Major Revision. the next 8 bits are the Minor Revision. The 12 least
        significant bits are the Build Number.
        
        :returns: FPGA Revision number.
        """
        return hal.getFPGARevision()

    @staticmethod
    def getFPGATime() -> int:
        """Read the microsecond timer from the FPGA.
        
        :returns: The current time in microseconds according to the FPGA.
        """
        return hal.getFPGATime()

    @staticmethod
    def getUserButton() -> bool:
        """Get the state of the "USER" button on the roboRIO.
        
        :returns: true if the button is currently pressed down
        """
        return hal.getFPGAButton()

    @staticmethod
    def getBatteryVoltage() -> float:
        """Read the battery voltage.
        
        :returns: The battery voltage in Volts.
        """
        return hal.getVinVoltage()

    @staticmethod
    def isSysActive() -> bool:
        """Gets a value indicating whether the FPGA outputs are enabled. The outputs may be disabled if
        the robot is disabled or e-stopped, the watchdog has expired, or if the roboRIO browns out.
        
        :returns: True if the FPGA outputs are enabled.
        """
        return hal.getSystemActive()

    @staticmethod
    def isBrownedOut() -> bool:
        """Check if the system is browned out.
        
        :returns: True if the system is browned out
        """
        return hal.getBrownedOut()

    @staticmethod
    def getInputVoltage() -> float:
        """Get the input voltage to the robot controller.
        
        :returns: The controller input voltage value in Volts
        """
        return hal.getVinVoltage()

    @staticmethod
    def getInputCurrent() -> float:
        """Get the input current to the robot controller.
        
        :returns: The controller input current value in Amps
        """
        return hal.getVinCurrent()

    @staticmethod
    def getVoltage3V3() -> float:
        """Get the voltage of the 3.3V rail.
        
        :returns: The controller 3.3V rail voltage value in Volts
        """
        return hal.getUserVoltage3V3()

    @staticmethod
    def getCurrent3V3() -> float:
        """Get the current output of the 3.3V rail.
        
        :returns: The controller 3.3V rail output current value in Volts
        """
        return hal.getUserCurrent3V3()

    @staticmethod
    def getEnabled3V3() -> bool:
        """Get the enabled state of the 3.3V rail. The rail may be disabled due to a controller brownout,
        a short circuit on the rail, or controller over-voltage.
        
        :returns: The controller 3.3V rail enabled value
        """
        return hal.getUserActive3V3()

    @staticmethod
    def getFaultCount3V3() -> int:
        """Get the count of the total current faults on the 3.3V rail since the controller has booted.
        
        :returns: The number of faults
        """
        return hal.getUserCurrentFaults3V3()

    @staticmethod
    def getVoltage5V() -> float:
        """Get the voltage of the 5V rail.
        
        :returns: The controller 5V rail voltage value in Volts
        """
        return hal.getUserVoltage5V()

    @staticmethod
    def getCurrent5V() -> float:
        """Get the current output of the 5V rail.
        
        :returns: The controller 5V rail output current value in Amps
        """
        return hal.getUserCurrent5V()

    @staticmethod
    def getEnabled5V() -> bool:
        """Get the enabled state of the 5V rail. The rail may be disabled due to a controller brownout, a
        short circuit on the rail, or controller over-voltage.
        
        :returns: The controller 5V rail enabled value
        """
        return hal.getUserActive5V()

    @staticmethod
    def getFaultCount5V() -> int:
        """Get the count of the total current faults on the 5V rail since the controller has booted.
        
        :returns: The number of faults
        """
        return hal.getUserCurrentFaults5V()

    @staticmethod
    def getVoltage6V() -> float:
        """Get the voltage of the 6V rail.
        
        :returns: The controller 6V rail voltage value in Volts
        """
        return hal.getUserVoltage6V()

    @staticmethod
    def getCurrent6V() -> float:
        """Get the current output of the 6V rail.
        
        :returns: The controller 6V rail output current value in Amps
        """
        return hal.getUserCurrent6V()

    @staticmethod
    def getEnabled6V() -> bool:
        """Get the enabled state of the 6V rail. The rail may be disabled due to a controller brownout, a
        short circuit on the rail, or controller over-voltage.
        
        :returns: The controller 6V rail enabled value
        """
        return hal.getUserActive6V()

    @staticmethod
    def getFaultCount6V() -> int:
        """Get the count of the total current faults on the 6V rail since the controller has booted.
        
        :returns: The number of faults
        """
        return hal.getUserCurrentFaults6V()

    @staticmethod
    def getCANStatus() -> Tuple[float, int, int, int, int]:
        """Get the current status of the CAN bus.

        :returns: The status of the CAN bus as a tuple: "percentBusUtilization", "busOffCount", "txFullCount", "receiveErrorCount", "transmitErrorCount"
        """
        return hal.CAN_GetCANStatus()
