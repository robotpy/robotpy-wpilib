# validated: 2018-01-06 TW f9bece2ffbf7 edu/wpi/first/wpilibj/Sendable.java

from .sendablebuilder import SendableBuilder

__all__ = ["Sendable"]


class Sendable:
    """The base interface for objects that can be sent over the network
    through network tables"""

    def getName(self) -> str:
        """
        Gets the name of this Sendable object.

        :returns: Name
        :rtype: str
        """
        raise NotImplementedError

    def setName(self, subsystem: str, name: str = None) -> None:
        """
        Sets the name of this Sendable object.

        :param name: Name
        :type name: str
        """
        raise NotImplementedError

    def _setNameAndSubsystem(self, subsystem: str, name: str) -> None:
        """
        Sets both the subsystem name and device name of this Sendable object.

        :param subsystem: subsystem name
        :type subsystem: str
        :param name: Name
        :type name: str
        """
        self.setSubsystem(subsystem)
        self.setName(name)

    def getSubsystem(self) -> str:
        """
        Gets the subsystem name of this Sendable object.

        :returns: subsystem name
        :rtype: str
        """
        raise NotImplementedError

    def setSubsystem(self, subsystem: str) -> None:
        """
        Sets the subsystem name of this Sendable object.

        :param subsystem: subsystem name
        :type subsystem: str
        """
        raise NotImplementedError

    def initSendable(self, builder: SendableBuilder) -> None:
        """
        Initializes this Sendable object.

        :param builder: sendable builder
        """
        raise NotImplementedError
