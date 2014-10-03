class Sendable:
    """The base interface for objects that can be sent over the network
    through network tables."""

    def initTable(self, subtable):
        """Initializes a table for this sendable object.

        :param subtable: The table to put the values in.
        """
        raise NotImplementedError

    def getTable(self):
        """:returns: the table that is currently associated with the sendable
        """
        raise NotImplementedError

    def getSmartDashboardType(self):
        """:returns: the string representation of the named data type that
            will be used by the smart dashboard for this sendable
        """
        raise NotImplementedError
