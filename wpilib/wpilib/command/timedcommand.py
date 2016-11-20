# validated: 2016-11-20 KC b25a7cb3704d shared/java/edu/wpi/first/wpilibj/command/TimedCommand.java
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
        super().__init__(name, timeoutInSeconds)


    def isFinished(self):
        return self.isTimedOut()
