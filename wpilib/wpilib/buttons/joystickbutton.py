# validated: 2017-10-19 AA e1195e8b9dab edu/wpi/first/wpilibj/buttons/JoystickButton.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .button import Button
from ..interfaces.generichid import GenericHID

__all__ = ["JoystickButton"]


class JoystickButton(Button):
    """A :class:`.button.Button` that gets its state from a :class:`.GenericHID`."""

    def __init__(self, joystick: GenericHID, buttonNumber: int) -> None:
        """Create a joystick button for triggering commands.

        :param joystick: The GenericHID object that has the button (e.g.
                         :class:`.Joystick`, :class:`.KinectStick`, etc)
        :param buttonNumber: The button number
                             (see :meth:`.GenericHID.getRawButton`)
        """
        super().__init__()
        self.joystick = joystick
        self.buttonNumber = buttonNumber

    def get(self) -> bool:
        """Gets the value of the joystick button.

        :returns: The value of the joystick button
        """
        return self.joystick.getRawButton(self.buttonNumber)
