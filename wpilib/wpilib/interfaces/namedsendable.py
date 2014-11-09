from ..sendable import Sendable

__all__ = ["NamedSendable"]

class NamedSendable(Sendable):
    """The interface for sendable objects that gives the sendable a default
    name in the Smart Dashboard.
    """

    def getName(self):
        """
            :returns: The name of the subtable of SmartDashboard that the
                      :class:`.Sendable` object will use
        """
        raise NotImplementedError
