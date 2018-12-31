# validated: 2017-12-21 DV de134a5c608d edu/wpi/first/wpilibj/NamedSendable.java
# ----------------------------------------------------------------------------
# Copyright (c) 2012-2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import warnings

from ..command.subsystem import Subsystem
from ..sendable import Sendable
from ..sendablebuilder import SendableBuilder

__all__ = ["NamedSendable"]


class NamedSendable(Sendable):
    """The interface for sendable objects that gives the sendable a default
    name in the Smart Dashboard.

    .. deprecated:: 2018.0
        Use :class:`.Sendable` directly instead.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        warnings.warn(
            "NamedSendable is deprecated, use Sendable directly instead",
            DeprecationWarning,
            stacklevel=2,
        )

    def getName(self) -> str:
        """The name of the subtable.

        :returns: The name of the subtable of SmartDashboard that the
                  :class:`.Sendable` object will use
        """
        raise NotImplementedError

    def setName(self, name: str) -> None:
        pass

    def getSubsystem(self) -> str:
        return ""

    def setSubsystem(self, subsystem: Subsystem) -> None:
        pass

    def initSendable(self, builder: SendableBuilder) -> None:
        pass
