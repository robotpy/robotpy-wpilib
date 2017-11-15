# validated: 2017-10-07 EN e1195e8b9dab edu/wpi/first/wpilibj/livewindow/LiveWindowSendable.java

from networktables import NetworkTables
from .sendable import Sendable

__all__ = ["LiveWindowSendable"]

class LiveWindowSendable(Sendable):
    """A special type of object that can be displayed on the live window.
    """

    def updateTable(self):
        """Update the table for this sendable object with the latest
        values.
        """
        pass

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
