# validated: 2017-10-18 AA e1195e8b9dab edu/wpi/first/wpilibj/buttons/InternalButton.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .button import Button

__all__ = ["InternalButton"]


class InternalButton(Button):
    """This class is intended to be used within a program.  The programmer can
    manually set its value.
    Also includes a setting for whether or not it should invert its value.
    """

    def __init__(self, inverted: bool = False) -> None:
        """Creates an InternalButton which is inverted depending on the input.

        :param inverted: If False, then this button is pressed when set to
                         True, otherwise it is pressed when set to False.
        """
        self.pressed = inverted
        self.inverted = inverted

    def setInverted(self, inverted: bool) -> None:
        self.inverted = inverted

    def setPressed(self, pressed: bool) -> None:
        self.pressed = pressed

    def get(self) -> int:
        return self.pressed ^ self.inverted
