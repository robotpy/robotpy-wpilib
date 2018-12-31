# validated: 2017-11-13 TW 21585f70a88e edu/wpi/first/wpilibj/GamepadBase.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
import warnings
from typing import Optional

from .generichid import GenericHID

__all__ = ["GamepadBase"]


class GamepadBase(GenericHID):
    """
    GamepadBase Interface.

    .. deprecated: 2018.0.0
       Inherit directly from :class:`.GenericHID` instead.
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        warnings.warn(
            "GamepadBase is deprecated, inherit directly from GenericHID instead",
            DeprecationWarning,
            stacklevel=2,
        )

    def getRawAxis(self, axis: int) -> float:
        raise NotImplementedError

    def getBumper(self, hand: GenericHID.Hand) -> bool:
        """Is the bumper pressed.

        :param hand: which hand
        :returns: true if the bumper is pressed
        """
        raise NotImplementedError

    def getStickButton(self, hand: Optional[GenericHID.Hand] = None) -> bool:
        raise NotImplementedError

    def getRawButton(self, button: int) -> bool:
        raise NotImplementedError

    def getPOV(self, pov: int = 0) -> int:
        raise NotImplementedError

    def getPOVCount(self) -> int:
        raise NotImplementedError

    def getType(self) -> GenericHID.HIDType:
        raise NotImplementedError

    def getName(self) -> str:
        raise NotImplementedError

    def setOutput(self, outputNumber: int, value: bool) -> None:
        raise NotImplementedError

    def setOutputs(self, value: bool) -> bool:
        raise NotImplementedError

    def setRumble(self, type: GenericHID.RumbleType, value: float) -> bool:
        raise NotImplementedError
