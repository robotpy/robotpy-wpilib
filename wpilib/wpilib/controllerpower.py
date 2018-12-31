# validated: 2018-01-04 TW 8b7aa61091df edu/wpi/first/wpilibj/ControllerPower.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

__all__ = ["ControllerPower"]


class ControllerPower:
    """Old Controller PR class.

    .. deprecated:: 2018.0.0
        Use RobotController class instead
    """

    @staticmethod
    def getInputVoltage() -> float:
        """
            Get the input voltage to the robot controller

            :returns: The controller input voltage value in Volts
        """
        return hal.getVinVoltage()

    @staticmethod
    def getInputCurrent() -> float:
        """
            Get the input current to the robot controller

            :returns: The controller input current value in Amps
        """
        return hal.getVinCurrent()

    @staticmethod
    def getVoltage3V3() -> float:
        """
            Get the voltage of the 3.3V rail

            :returns: The controller 3.3V rail voltage value in Volts
        """
        return hal.getUserVoltage3V3()

    @staticmethod
    def getCurrent3V3() -> float:
        """
            Get the current output of the 3.3V rail

            :returns: The controller 3.3V rail output current value in Amps
        """
        return hal.getUserCurrent3V3()

    @staticmethod
    def getEnabled3V3() -> bool:
        """
            Get the enabled state of the 3.3V rail. The rail may be
            disabled due to a controller brownout, a short circuit on the
            rail, or controller over-voltage

            :returns: True if enabled, False otherwise
        """
        return hal.getUserActive3V3()

    @staticmethod
    def getFaultCount3V3() -> int:
        """
            Get the count of the total current faults on the 3.3V rail since
            the controller has booted

            :returns: The number of faults
        """
        return hal.getUserCurrentFaults3V3()

    @staticmethod
    def getVoltage5V() -> float:
        """
            Get the voltage of the 5V rail


            :returns: The controller 5V rail voltage value in Volts
        """
        return hal.getUserVoltage5V()

    @staticmethod
    def getCurrent5V() -> float:
        """
            Get the current output of the 5V rail

            :returns: The controller 5V rail output current value in Amps
        """
        return hal.getUserCurrent5V()

    @staticmethod
    def getEnabled5V() -> bool:
        """
            Get the enabled state of the 5V rail. The rail may be disabled
            due to a controller brownout, a short circuit on the rail, or
            controller over-voltage

            :returns: True if enabled, False otherwise
        """
        return hal.getUserActive5V()

    @staticmethod
    def getFaultCount5V() -> int:
        """
            Get the count of the total current faults on the 5V rail since
            the controller has booted

            :returns: The number of faults
        """
        return hal.getUserCurrentFaults5V()

    @staticmethod
    def getVoltage6V() -> float:
        """
            Get the voltage of the 6V rail

            :returns: The controller 6V rail voltage value in Volts
        """
        return hal.getUserVoltage6V()

    @staticmethod
    def getCurrent6V() -> float:
        """
            Get the current output of the 6V rail

            :returns: The controller 6V rail output current value in Amps
        """
        return hal.getUserCurrent6V()

    @staticmethod
    def getEnabled6V() -> bool:
        """
            Get the enabled state of the 6V rail. The rail may be disabled
            due to a controller brownout, a short circuit on the rail, or
            controller over-voltage

            :returns: True if enabled, False otherwise
        """
        return hal.getUserActive6V()

    @staticmethod
    def getFaultCount6V() -> int:
        """
            Get the count of the total current faults on the 6V rail since
            the controller has booted

            :returns: The number of faults
        """
        return hal.getUserCurrentFaults6V()
