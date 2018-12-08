# validated: 2018-10-30 EN 0b113ad9ce93 edu/wpi/first/wpilibj/command/TimedCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command

__all__ = ["TimedCommand"]


class TimedCommand(Command):
    """A command that runs for a set period of time."""

    def __init__(self, name, timeoutInSeconds, subsystem=None):
        """Instantiates a TimedCommand with the given name and timeout.

        :param name: the name of the command
        :param timeoutInSeconds: the time the command takes to run
        :param subsystem: the subsystem that this command requires
        """
        super().__init__(name, timeoutInSeconds, subsystem)

    def isFinished(self):
        """Ends command when timed out."""
        return self.isTimedOut()
