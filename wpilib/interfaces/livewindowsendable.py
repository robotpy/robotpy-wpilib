from .sendable import Sendable

class LiveWindowSendable(Sendable):
    """Live Window Sendable is a special type of object sendable to the live
    window.
    """

    def updateTable(self):
        """Update the table for this sendable object with the latest
        values.
        """
        raise NotImplementedError

    def startLiveWindowMode(self):
        """Start having this sendable object automatically respond to
        value changes reflect the value on the table.
        """
        raise NotImplementedError

    def stopLiveWindowMode(self):
        """Stop having this sendable object automatically respond to value
        changes.
        """
        raise NotImplementedError
