# validated: 2017-12-21 DV de134a5c608d edu/wpi/first/wpilibj/livewindow/LiveWindowSendable.java
# ----------------------------------------------------------------------------
# Copyright (c) 2008-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import warnings

from .command.subsystem import Subsystem
from networktables import NetworkTables
from .sendable import Sendable
from .sendablebuilder import SendableBuilder

__all__ = ["LiveWindowSendable"]


class LiveWindowSendable(Sendable):
    """A special type of object that can be displayed on the live window.

    .. deprecated:: 2018.0
        Use :class:`.Sendable` directly instead.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        warnings.warn(
            "LiveWindowSendable is deprecated, use Sendable directly instead",
            DeprecationWarning,
            stacklevel=2,
        )

    def updateTable(self) -> None:
        """Update the table for this sendable object with the latest
        values.
        """
        raise NotImplementedError

    def startLiveWindowMode(self) -> None:
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
                NetworkTables.NotifyFlags.IMMEDIATE
                | NetworkTables.NotifyFlags.NEW
                | NetworkTables.NotifyFlags.UPDATE,
            )

    def stopLiveWindowMode(self) -> None:
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

    def getName(self) -> str:
        return ""

    def _setName(self, name: str) -> None:
        pass

    def getSubsystem(self) -> str:
        return ""

    def setSubsystem(self, subsystem: Subsystem) -> None:
        pass

    def initSendable(self, builder: SendableBuilder) -> None:
        builder.setUpdateTable(self.updateTable)
