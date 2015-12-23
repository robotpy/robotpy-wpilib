# validated: 2015-12-22 DS 6d854af shared/java/edu/wpi/first/wpilibj/buttons/InternalButton.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .button import Button

__all__ = ["InternalButton"]

class InternalButton(Button):
    """This class is intended to be used within a program.  The programmer can
    manually set its value. Includes a setting for whether or not it should
    invert its value.
    """

    def __init__(self, inverted=False):
        """Creates an InternalButton which is inverted depending on the input.

        :param inverted: If False, then this button is pressed when set to
                         True, otherwise it is pressed when set to False.
        """
        self.pressed = inverted
        self.inverted = inverted

    def setInverted(self, inverted):
        self.inverted = inverted

    def setPressed(self, pressed):
        self.pressed = pressed

    def get(self):
        return self.pressed ^ self.inverted
