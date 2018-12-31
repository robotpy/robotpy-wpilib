# validated: 2018-01-06 TW f9bece2ffbf7 edu/wpi/first/wpilibj/Sendable.java
from typing import Optional

from .sendablebuilder import SendableBuilder

__all__ = ["Sendable"]


class Sendable:
    """The base interface for objects that can be sent over the network
    through network tables"""

    def getName(self) -> str:
        """
        Gets the name of this Sendable object.

        :returns: Name
        """
        raise NotImplementedError

    def setName(self, subsystem: str, name: Optional[str] = None) -> None:
        """
        Sets the name (and optionally the subsystem name) of this Sendable object.

        This may be called with two different sets of parameters:

        - name
        - subsystem, name

        :param str subsystem: subsystem name
        :param str name: Name
        """
        if name is None:
            self._setName(subsystem)
        else:
            self._setNameAndSubsystem(subsystem, name)

    def _setName(self, name: str) -> None:
        """Sets the name of this Sendable object."""
        raise NotImplementedError

    def _setNameAndSubsystem(self, subsystem: str, name: str) -> None:
        """
        Sets both the subsystem name and device name of this Sendable object.

        :param subsystem: subsystem name
        :param name: Name
        """
        self.setSubsystem(subsystem)
        self.setName(name)

    def getSubsystem(self) -> str:
        """
        Gets the subsystem name of this Sendable object.

        :returns: subsystem name
        """
        raise NotImplementedError

    def setSubsystem(self, subsystem: str) -> None:
        """
        Sets the subsystem name of this Sendable object.

        :param subsystem: subsystem name
        """
        raise NotImplementedError

    def initSendable(self, builder: SendableBuilder) -> None:
        """
        Initializes this Sendable object.

        :param builder: sendable builder
        """
        raise NotImplementedError
