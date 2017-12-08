# validated: 2017-10-03 EN 34c18ef00062 edu/wpi/first/wpilibj/Sendable.java

__all__ = ["Sendable"]

class Sendable:
    """The base interface for objects that can be sent over the network
    through network tables"""
    
    def getName(self):
        """
        Gets the name of this Sendable object.

        :returns: Name
        :rtype: str
        """
        raise NotImplementedError

    def setName(self, subsystem, name=None):
        """
        Sets the name of this Sendable object.

        :param name: Name
        :type name: str
        """
        raise NotImplementedError

    def _setNameAndSubsystem(self, subsystem, name):
        """
        Sets both the subsystem name and device name of this Sendable object.

        :param subsystem: subsystem name
        :type subsystem: str
        :param name: Name
        :type name: str
        """
        self.setSubsystem(subsystem)
        self.setName(name)

    def getSubsystem(self):
        """
        Gets the subsystem name of this Sendable object.

        :returns: subsystem name
        :rtype: str
        """
        raise NotImplementedError

    def setSubsystem(self, subsystem):
        """
        Sets the subsystem name of this Sendable object.

        :param subsystem: subsystem name
        :type subsystem: str
        """
        raise NotImplementedError

    def initSendable(self, builder):
        """
        Initializes this Sendable object.

        :param builder: sendable builder
        :type builder: :class:`wpilib.SendableBuilder`
        """
        raise NotImplementedError

    # todo: remove
    def initTable(self, subtable):
        """Initializes a table for this sendable object.

        :param subtable: The table to put the values in.
        """
        if hasattr(self, "updateTable"):
            self.updateTable()
