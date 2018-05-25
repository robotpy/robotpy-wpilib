# validated: 2017-10-17 AA e1195e8b9dab edu/wpi/first/wpilibj/buttons/Button.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from ..command import command
from .trigger import Trigger

__all__ = ["Button"]


class Button(Trigger):
    """This class provides an easy way to link commands to OI inputs.

    It is very easy to link a button to a command.  For instance, you could
    link the trigger button of a joystick to a "score" command.

    This class represents a subclass of :class:`.Trigger` that is specifically aimed at
    buttons on an operator interface as a common use case of the more
    generalized Trigger objects. This is a simple wrapper around Trigger with
    the method names renamed to fit the Button object use.
    """

    def whenPressed(self, command: "command.Command") -> None:
        """Starts the given command whenever the button is newly pressed.

        :param command: the command to start
        """
        self.whenActive(command)

    def whileHeld(self, command: "command.Command") -> None:
        """Constantly starts the given command while the button is held.

        :meth:`.Command.start` will be called repeatedly while the button is
        held, and will be canceled when the button is released.

        :param command: the command to start
        """
        self.whileActive(command)

    def whenReleased(self, command: "command.Command") -> None:
        """Starts the command when the button is released.

        :param command: the command to start
        """
        self.whenInactive(command)

    def toggleWhenPressed(self, command: "command.Command") -> None:
        """Toggles the command whenever the button is pressed (on then off
        then on).

        :param command:
        """
        self.toggleWhenActive(command)

    def cancelWhenPressed(self, command: "command.Command") -> None:
        """Cancel the command when the button is pressed.

        :param command:
        """
        self.cancelWhenActive(command)
