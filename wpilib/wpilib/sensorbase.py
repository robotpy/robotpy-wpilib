#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .livewindowsendable import LiveWindowSendable

__all__ = ["SensorBase"]

class SensorBase(LiveWindowSendable): # TODO: Refactor
    """Base class for all sensors
    
    Stores most recent status information as well as containing utility
    functions for checking channels and error processing.
    """

    # TODO: Move this to the HAL

    #: Ticks per microsecond
    kSystemClockTicksPerMicrosecond = 40
    
    #: Number of digital channels per roboRIO
    kDigitalChannels = 26
    
    #: Number of analog input channels
    kAnalogInputChannels = 8
    
    #: Number of analog output channels
    kAnalogOutputChannels = 2
    
    #: Number of solenoid channels per module
    kSolenoidChannels = 8
    
    #: Number of solenoid modules
    kSolenoidModules = 2
    
    #: Number of PWM channels per roboRIO
    kPwmChannels = 20
    
    #: Number of relay channels per roboRIO
    kRelayChannels = 4
    
    #: Number of power distribution channels
    kPDPChannels = 16

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
        pass
        #if hal.checkSolenoidModule(moduleNumber - 1) != 0:
        #    print("Solenoid module %d is not present." % moduleNumber)

    @staticmethod
    def checkDigitalChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kDigitalChannels:
            raise IndexError("Requested digital channel number %d is out of range." % channel)

    @staticmethod
    def checkRelayChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kRelayChannels:
            raise IndexError("Requested relay channel number %d is out of range." % channel)

    @staticmethod
    def checkPWMChannel(channel):
        """Check that the digital channel number is valid.
        Verify that the channel number is one of the legal channel numbers.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kPwmChannels:
            raise IndexError("Requested PWM channel number %d is out of range." % channel)

    @staticmethod
    def checkAnalogInputChannel(channel):
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kAnalogInputChannels:
            raise IndexError("Requested analog input channel number %d is out of range." % channel)

    @staticmethod
    def checkAnalogOutputChannel(channel):
        """Check that the analog input number is value.
        Verify that the analog input number is one of the legal channel
        numbers.  Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kAnalogOutputChannels:
            raise IndexError("Requested analog output channel number %d is out of range." % channel)

    @staticmethod
    def checkSolenoidChannel(channel):
        """Verify that the solenoid channel number is within limits.  Channel
        numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kSolenoidChannels:
            raise IndexError("Requested solenoid channel number %d is out of range." % channel)

    @staticmethod
    def checkPDPChannel(channel):
        """Verify that the power distribution channel number is within limits.
        Channel numbers are 0-based.

        :param channel: The channel number to check.
        """
        if channel < 0 or channel >= SensorBase.kPDPChannels:
            raise IndexError("Requested PDP channel number %d is out of range." % channel)

    @staticmethod
    def getDefaultSolenoidModule():
        """Get the number of the default solenoid module.

        :returns: The number of the default solenoid module.
        """
        return SensorBase.defaultSolenoidModule

    def free(self):
        """Free the resources used by this object"""
        # TODO: delete?
        pass
