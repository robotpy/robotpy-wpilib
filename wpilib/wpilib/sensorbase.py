# validated: 2018-01-01 EN f9bece2ffbf7 edu/wpi/first/wpilibj/SensorBase.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

from .sendablebase import SendableBase

__all__ = ["SensorBase"]

class SensorBase(SendableBase):
    """Base class for all sensors
    
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

    #: Number of power distribution channels per PDP
    kPDPModules = hal.getNumPDPModules()

    #: Number of PCM modules
    kPCMModules = hal.getNumPCMModules()

    #: Default solenoid module
    defaultSolenoidModule = 0

    @staticmethod
    def setDefaultSolenoidModule(moduleNumber):
        """Set the default location for the Solenoid module.

        :param moduleNumber: The number of the solenoid module to use.
        """
        SensorBase.checkSolenoidModule(moduleNumber)
        SensorBase.defaultSolenoidModule = moduleNumber

    @staticmethod
    def checkSolenoidModule(moduleNumber):
        """Verify that the solenoid module is correct.

        :param moduleNumber: The solenoid module module number to check.
        """
        if not hal.checkSolenoidModule(moduleNumber):
            raise IndexError("Requested solenoid module number %d is out of range [0, %d)." % (moduleNumber, SensorBase.kPCMModules))

    @staticmethod
    def checkDigitalChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkDIOChannel(channel):
            raise IndexError("Requested digital channel number %d is out of range [0, %d)." % (channel, SensorBase.kDigitalChannels))

    @staticmethod
    def checkRelayChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkRelayChannel(channel):
            raise IndexError("Requested relay channel number %d is out of range [0, %d)." % (channel, SensorBase.kRelayChannels))

    @staticmethod
    def checkPWMChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkPWMChannel(channel):
            raise IndexError("Requested PWM channel number %d is out of range [0, %d)." % (channel, SensorBase.kPwmChannels))

    @staticmethod
    def checkAnalogInputChannel(channel):
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkAnalogInputChannel(channel):
            raise IndexError("Requested analog input channel number %d is out of range [0, %d)." % (channel, SensorBase.kAnalogInputChannels))

    @staticmethod
    def checkAnalogOutputChannel(channel):
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkAnalogOutputChannel(channel):
            raise IndexError("Requested analog output channel number %d is out of range [0, %d)." % (channel, SensorBase.kAnalogOutputChannels))

    @staticmethod
    def checkSolenoidChannel(channel):
        """Verify that the solenoid channel number is within limits.  Channel
        numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkSolenoidChannel(channel):
            raise IndexError("Requested solenoid channel number %d is out of range [0, %d)." % (channel, SensorBase.kSolenoidChannels))

    @staticmethod
    def checkPDPChannel(channel):
        """Verify that the power distribution channel number is within limits.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if not hal.checkPDPChannel(channel):
            raise IndexError("Requested PDP channel number %d is out of range [0, %d)." % (channel, SensorBase.kPDPChannels))

    @staticmethod
    def checkPDPModule(module):
        """Verify that the power distribution module number is within limits.
        Module numbers are 0-based.

        :param module: The module number to check.
        """
        if not hal.checkPDPModule(module):
            raise IndexError("Requested PDP module number %d is out of range [0, %d)." % (module, SensorBase.kPDPModules))

    @staticmethod
    def getDefaultSolenoidModule():
        """Get the number of the default solenoid module.

        :returns: The number of the default solenoid module.
        """
        return SensorBase.defaultSolenoidModule
