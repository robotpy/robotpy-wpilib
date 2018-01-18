# validated: 2017-12-21 DV de134a5c608d edu/wpi/first/wpilibj/livewindow/LiveWindowSendable.java
#----------------------------------------------------------------------------
# Copyright (c) 2008-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import warnings

from networktables import NetworkTables
from .sendable import Sendable

__all__ = ["LiveWindowSendable"]

class LiveWindowSendable(Sendable):
    """A special type of object that can be displayed on the live window.

    .. deprecated:: 2018.0
        Use :class:`.Sendable` directly instead.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        warnings.warn('LiveWindowSendable is deprecated, use Sendable directly instead',
                      DeprecationWarning, stacklevel=2)

    def updateTable(self):
        """Update the table for this sendable object with the latest
        values.
        """
        raise NotImplementedError

    def startLiveWindowMode(self):
        """Start having this sendable object automatically respond to
        value changes reflect the value on the table.

        Default implementation will add self.valueChanged (if it exists)
        as a table listener on "Value".
        """
        if hasattr(self, "valueChanged"):
            valueEntry = getattr(self, "valueEntry", None)
            valueListener = getattr(self, "valueListener", None)
            if valueEntry is None or valueListener is not None:
                return
            self.valueListener = valueEntry.addListener(
                self.valueChanged, 
                NetworkTables.NotifyFlags.IMMEDIATE |
                NetworkTables.NotifyFlags.NEW |
                NetworkTables.NotifyFlags.UPDATE)

    def stopLiveWindowMode(self):
        """Stop having this sendable object automatically respond to value
        changes.
        """
        # TODO: Broken, should only remove the listener from "Value" only.
        valueEntry = getattr(self, "valueEntry", None)
        valueListener = getattr(self, "valueListener", None)
        if valueEntry is None or valueListener is None:
            return
        valueEntry.removeListener(valueListener)
        self.valueListener = None

    def getName(self):
        return ""

    def _setName(self, name):
        pass

    def getSubsystem(self):
        return ""

    def setSubsystem(self, subsystem):
        pass

    def initSendable(self, builder):
        builder.setUpdateTable(self.updateTable)
