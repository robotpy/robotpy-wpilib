# validated: 2018-10-30 EN 8b5dc53cc7cd edu/wpi/first/wpilibj/command/InstantCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from .command import Command

__all__ = ["InstantCommand"]


class InstantCommand(Command):
    """
    This command will execute once, then finish immediately afterward.

    Subclassing :class:`.InstantCommand` is shorthand for returning true from
    :meth:`.Command.isFinished`
    """

    def __init__(self, name=None, subsystem=None, func=None):
        """
        Creates a new InstantCommand

        :param name:        the name for this command
        :param requirement: the subsystem this command requires
        :param func:        the function to run when :meth:`.Command.initialize` is run
        """
        super().__init__(name, subsystem=subsystem)
        self.func = func

    def isFinished(self):
        return True

    def _initialize(self):
        """
        Trigger the stored function.

        Called just before this Command runs the first time.
        """
        super()._initialize()
        if self.func is not None:
            self.func()
