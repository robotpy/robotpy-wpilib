#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .command import Command

__all__ = ["StartCommand"]

class StartCommand(Command):
    """A StartCommand will call the start() method of another command when it
    is initialized and will finish immediately.
    """

    def __init__(self, commandToStart):
        """Instantiates a StartCommand which will start the
        given command whenever its initialize() is called.

        :param commandToStart: the :class:`.Command` to start
        """
        super().__init__("Start(%s)" % commandToStart)
        self.commandToFork = commandToStart

    def initialize(self):
        self.commandToFork.start()

    def isFinished(self):
        return True
