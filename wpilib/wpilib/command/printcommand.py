# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/PrintCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .instantcommand import InstantCommand

__all__ = ["PrintCommand"]


class PrintCommand(InstantCommand):
    """A PrintCommand is a command which prints out a string when it is
    initialized, and then immediately finishes.

    It is useful if you want a :class:`.CommandGroup` to print out a string when it
    reaches a certain point.
    """

    def __init__(self, message: str) -> None:
        """Instantiates a PrintCommand which will print the given message when
        it is run.
        
        :param message: the message to print
        """
        super().__init__('Print("%s")' % message)
        self.message = message

    def initialize(self) -> None:
        print(self.message)
