#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .command import Command

__all__ = ["PrintCommand"]

class PrintCommand(Command):
    """A PrintCommand is a command which prints out a string when it is
    initialized, and then immediately finishes.

    It is useful if you want a :class:`.CommandGroup` to print out a string when it
    reaches a certain point.
    """

    def __init__(self, message):
        """Instantiates a PrintCommand which will print the given message when
        it is run.
        
        :param message: the message to print
        """
        super().__init__('Print("%s")' % message)
        self.message = message

    def initialize(self):
        print(self.message)

    def isFinished(self):
        return True
