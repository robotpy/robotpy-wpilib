# validated: 2017-10-03 EN 34c18ef00062 edu/wpi/first/wpilibj/Sendable.java

__all__ = ["Sendable"]

class Sendable:
    """The base interface for objects that can be sent over the network
    through network tables"""

    def initTable(self, subtable):
        """Initializes a table for this sendable object.

        :param subtable: The table to put the values in.
        """
        if hasattr(self, "updateTable"):
            self.updateTable()

    def getSmartDashboardType(self):
        """
            :returns: the string representation of the named data type that
                will be used by the smart dashboard for this sendable
        """
        raise NotImplementedError
