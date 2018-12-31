# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/StartCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command
from .instantcommand import InstantCommand

__all__ = ["StartCommand"]


class StartCommand(InstantCommand):
    """A StartCommand will call the start() method of another command when it
    is initialized and will finish immediately.
    """

    def __init__(self, commandToStart: Command) -> None:
        """Instantiates a StartCommand which will start the
        given command whenever its initialize() is called.

        :param commandToStart: the :class:`.Command` to start
        """
        super().__init__("Start(%s)" % commandToStart)
        self.commandToFork = commandToStart

    def initialize(self) -> None:
        self.commandToFork.start()
