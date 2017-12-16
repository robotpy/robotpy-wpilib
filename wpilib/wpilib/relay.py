# validated: 2017-12-12 EN f9bece2ffbf7 edu/wpi/first/wpilibj/Relay.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import weakref
from enum import IntEnum

from .livewindow import LiveWindow
from .motorsafety import MotorSafety
from .resource import Resource
from .sensorbase import SensorBase
from .sendablebase import SendableBase

__all__ = ["Relay"]

def _freeRelay(*handles):
    for handle in handles:
        try:
            hal.setRelay(handle, False)
        except:
            pass
        if handle:
            hal.freeRelayPort(handle)

class Relay(SendableBase, MotorSafety):
    """Controls VEX Robotics Spike style relay outputs.
    
    Relays are intended to be connected to Spikes or similar relays. The relay
    channels controls a pair of channels that are either both off, one on, the
    other on, or both on. This translates into two Spike outputs at 0v, one at
    12v and one at 0v, one at 0v and the other at 12v, or two Spike outputs at
    12V. This allows off, full forward, or full reverse control of motors without
    variable speed. It also allows the two channels (forward and reverse) to
    be used independently for something that does not care about voltage
    polarity (like a solenoid).
    
    .. not_implemented: initRelay
    """

    relayChannels = Resource(SensorBase.kRelayChannels * 2)

    class Value(IntEnum):
        """The state to drive a Relay to."""
        
        #: Off
        kOff = 0
        
        #: On for relays with defined direction
        kOn = 1
        
        #: Forward
        kForward = 2
        
        #: Reverse
        kReverse = 3

        def getPrettyValue(self):
            return self.name[1:]

        @classmethod
        def getValueOf(cls, name):
            return getattr(cls, 'k' + name, cls.kOff)

    class Direction(IntEnum):
        """The Direction(s) that a relay is configured to operate in."""
        
        #: Both directions are valid
        kBoth = 0
        
        #: Only forward is valid
        kForward = 1
        
        #: Only reverse is valid
        kReverse = 2

    def __init__(self, channel, direction=None):
        """Relay constructor given a channel.

        Initially the relay is set to both lines at 0v.

        :param channel: The channel number for this relay (0-3)
        :type  channel: int
        :param direction: The direction that the Relay object will control.
            If not specified, defaults to allowing both directions.
        :type  direction: :class:`Relay.Direction`
        """
        super().__init__()
        if direction is None:
            direction = self.Direction.kBoth
        self.channel = channel
        self.direction = direction
        self._forwardHandle = None
        self._reverseHandle = None

        self._initRelay()
        
        self.set(self.Value.kOff)

        MotorSafety.__init__(self)

    def _initRelay(self):
        SensorBase.checkRelayChannel(self.channel)
        portHandle = hal.getPort(self.channel)

        try:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                Relay.relayChannels.allocate(self, self.channel * 2)
                self._forwardHandle = hal.initializeRelayPort(portHandle, True)
                hal.report(hal.UsageReporting.kResourceType_Relay, self.channel)

            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                Relay.relayChannels.allocate(self, self.channel * 2 + 1)
                self._reverseHandle = hal.initializeRelayPort(portHandle, False)
                hal.report(hal.UsageReporting.kResourceType_Relay, self.channel + 128)
        except IndexError as e:
            raise IndexError("Relay channel %d is already allocated" % self.channel) from e

        self.__finalizer = weakref.finalize(self, _freeRelay, self._forwardHandle, self._reverseHandle)

        self.setSafetyEnabled(False)
        
        self.setName("Relay", self.channel)

    @property
    def forwardHandle(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use relay after free() has been called")
        return self._forwardHandle

    @property
    def reverseHandle(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use relay after free() has been called")
        return self._reverseHandle

    def free(self):
        super().free()
        self.freeRelay()

    def freeRelay(self):
        self.__finalizer()
        Relay.relayChannels.free(self.channel * 2)
        Relay.relayChannels.free(self.channel * 2 + 1)
        self._forwardHandle = None
        self._reverseHandle = None

    def set(self, value):
        """Set the relay state.

        Valid values depend on which directions of the relay are controlled by
        the object.

        When set to kBothDirections, the relay can be set to any of the four
        states: 0v-0v, 12v-0v, 0v-12v, 12v-12v

        When set to kForwardOnly or kReverseOnly, you can specify the constant
        for the direction or you can simply specify kOff and kOn. Using only
        kOff and kOn is recommended.

        :param value: The state to set the relay.
        :type  value: :class:`Relay.Value`
        """
        if value == self.Value.kOff:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelay(self.forwardHandle, False)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelay(self.reverseHandle, False)
        elif value == self.Value.kOn:
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelay(self.forwardHandle, True)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelay(self.reverseHandle, True)
        elif value == self.Value.kForward:
            if self.direction == self.Direction.kReverse:
                raise ValueError("A relay configured for reverse cannot be set to forward")
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kForward):
                hal.setRelay(self.forwardHandle, True)
            if self.direction == self.Direction.kBoth:
                hal.setRelay(self.reverseHandle, False)
        elif value == self.Value.kReverse:
            if self.direction == self.Direction.kForward:
                raise ValueError("A relay configured for forward cannot be set to reverse")
            if self.direction == self.Direction.kBoth:
                hal.setRelay(self.forwardHandle, False)
            if (self.direction == self.Direction.kBoth or
                self.direction == self.Direction.kReverse):
                hal.setRelay(self.reverseHandle, True)
        else:
            raise ValueError("Invalid value argument '%s'" % value)

    def get(self):
        """Get the Relay State

        Gets the current state of the relay.

        When set to kForwardOnly or kReverseOnly, value is returned as kOn/kOff
        not kForward/kReverse (per the recommendation in Set)

        :returns: The current state of the relay
        :rtype: :class:`Relay.Value`
        """
        if self.direction == self.Direction.kForward:
            if hal.getRelay(self.forwardHandle):
                return self.Value.kOn
            else:
                return self.Value.kOff
        elif self.direction == self.Direction.kReverse:
            if hal.getRelay(self.reverseHandle):
                return self.Value.kOn
            else:
                return self.Value.kOff
        else:
            if hal.getRelay(self.forwardHandle):
                if hal.getRelay(self.reverseHandle):
                    return self.Value.kOn
                else:
                    return self.Value.kForward
            else:
                if hal.getRelay(self.reverseHandle):
                    return self.Value.kReverse
                else:
                    return self.Value.kOff

    def getChannel(self):
        """
        Get the channel number.

        :returns: The channel number.
        """
        return self.channel

    def stopMotor(self):
        self.set(self.Value.kOff)

    def getDescription(self):
        return "Relay ID {}".format(self.getChannel())

    def setDirection(self, direction):
        """Set the Relay Direction.

        Changes which values the relay can be set to depending on which
        direction is used.

        Valid inputs are kBothDirections, kForwardOnly, and kReverseOnly.

        :param direction: The direction for the relay to operate in
        :type  direction: :class:`Relay.Direction`
        """
        if self.direction == direction:
            return
        
        if direction not in list(self.Direction):
            raise ValueError("Invalid direction argument '%s'" % direction)

        self.freeRelay()
        self.direction = direction
        self._initRelay()

    def initSendable(self, builder):
        builder.setSmartDashboardType("Relay")
        builder.setSafeState(lambda: self.set(self.Value.kOff))
        builder.addStringProperty("Value", 
            lambda: self.get().getPrettyValue(), 
            lambda value: self.set(self.Value.getValueOf(value)))
