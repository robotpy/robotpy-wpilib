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
            table = getattr(self, "table", None)
            table_listener = getattr(self, "table_listener", None)
            if table is None or table_listener is not None:
                return
            self.table_listener = self.valueChanged
            table.addTableListener(self.valueChanged, True, key="Value")

    def stopLiveWindowMode(self):
        """Stop having this sendable object automatically respond to value
        changes.
        """
        # TODO: Broken, should only remove the listener from "Value" only.
        table = getattr(self, "table", None)
        table_listener = getattr(self, "table_listener", None)
        if table is None or table_listener is None:
            return
        table.removeTableListener(table_listener)
        self.table_listener = None
