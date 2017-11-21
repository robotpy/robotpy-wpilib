# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/TimedCommand.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

from .command import Command

__all__ = ["TimedCommand"]

class TimedCommand(Command):
    '''A command that runs for a set period of time.'''

    def __init__(self, name, timeoutInSeconds):
        """Instantiates a TimedCommand with the given name and timeout.

        :param name: the name of the command
        :param timeoutInSeconds: the time the command takes to run
        """
        super().__init__(name, timeoutInSeconds)


    def isFinished(self):
        """Ends command when timed out."""
        return self.isTimedOut()
