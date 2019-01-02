# validated: 2019-01-02 DV ecfe95383cdf edu/wpi/first/wpilibj/SensorUtil.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2018. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import hal

__all__ = ["SensorUtil"]


class SensorUtil:
    """
    Stores most recent status information as well as containing utility
    functions for checking channels and error processing.
    """

    #: Ticks per microsecond
    kSystemClockTicksPerMicrosecond = hal.getSystemClockTicksPerMicrosecond()

    #: Number of digital channels per roboRIO
    kDigitalChannels = hal.getNumDigitalChannels()

    #: Number of analog input channels per roboRIO
    kAnalogInputChannels = hal.getNumAnalogInputs()

    #: Number of analog output channels per roboRIO
    kAnalogOutputChannels = hal.getNumAnalogOutputs()

    #: Number of solenoid channels per module
    kSolenoidChannels = hal.getNumSolenoidChannels()

    #: Number of PWM channels per roboRIO
    kPwmChannels = hal.getNumPWMChannels()

    #: Number of relay channels per roboRIO
    kRelayChannels = hal.getNumRelayHeaders()

    #: Number of power distribution channels per PDP
    kPDPChannels = hal.getNumPDPChannels()

    #: Number of power distribution modules per PDP
    kPDPModules = hal.getNumPDPModules()

    #: Number of PCM modules
    kPCMModules = hal.getNumPCMModules()

    @staticmethod
    def checkSolenoidModule(moduleNumber: int) -> None:
        """Verify that the solenoid module is correct.

        :param moduleNumber: The solenoid module module number to check.
        """
        if not hal.checkSolenoidModule(moduleNumber):
            raise IndexError(
                "Requested solenoid module number %d is out of range [0, %d)."
                % (moduleNumber, SensorUtil.kPCMModules)
            )

    @staticmethod
    def checkDigitalChannel(channel: int) -> None:
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkDIOChannel(channel):
            raise IndexError(
                "Requested digital channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kDigitalChannels)
            )

    @staticmethod
    def checkRelayChannel(channel: int) -> None:
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkRelayChannel(channel):
            raise IndexError(
                "Requested relay channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kRelayChannels)
            )

    @staticmethod
    def checkPWMChannel(channel: int) -> None:
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkPWMChannel(channel):
            raise IndexError(
                "Requested PWM channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kPwmChannels)
            )

    @staticmethod
    def checkAnalogInputChannel(channel: int) -> None:
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkAnalogInputChannel(channel):
            raise IndexError(
                "Requested analog input channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kAnalogInputChannels)
            )

    @staticmethod
    def checkAnalogOutputChannel(channel: int) -> None:
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkAnalogOutputChannel(channel):
            raise IndexError(
                "Requested analog output channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kAnalogOutputChannels)
            )

    @staticmethod
    def checkSolenoidChannel(channel: int) -> None:
        """Verify that the solenoid channel number is within limits.  Channel
        numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkSolenoidChannel(channel):
            raise IndexError(
                "Requested solenoid channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kSolenoidChannels)
            )

    @staticmethod
    def checkPDPChannel(channel: int) -> None:
        """Verify that the power distribution channel number is within limits.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkPDPChannel(channel):
            raise IndexError(
                "Requested PDP channel number %d is out of range [0, %d)."
                % (channel, SensorUtil.kPDPChannels)
            )

    @staticmethod
    def checkPDPModule(module: int) -> None:
        """Verify that the power distribution module number is within limits.
        Module numbers are 0-based.

        :param module: The module number to check.
        """
        if not hal.checkPDPModule(module):
            raise IndexError(
                "Requested PDP module number %d is out of range [0, %d)."
                % (module, SensorUtil.kPDPModules)
            )

    @staticmethod
    def getDefaultSolenoidModule() -> int:
        """Get the number of the default solenoid module.

        :returns: The number of the default solenoid module.
        """
        return 0
