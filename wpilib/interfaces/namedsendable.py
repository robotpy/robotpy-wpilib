from .sendable import Sendable

class NamedSendable(Sendable):
    """The interface for sendable objects that gives the sendable a default
    name in the Smart Dashboard.
    """

    def getName(self):
        """:returns: The name of the subtable of SmartDashboard that the
        Sendable object will use
        """
        raise NotImplementedError
