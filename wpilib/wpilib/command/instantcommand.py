# validated: 2016-11-20 KC b25a7cb3704d shared/java/edu/wpi/first/wpilibj/command/InstantCommand.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------
from .command import Command

__all__ = ["InstantCommand"]

class InstantCommand(Command):
    '''
    A command that has no duration. Subclasses should implement the initialize()
    method to carry out desired actions.
    '''

    def __init__(self, name):
        super().__init__(name)


    def isFinished(self):
        return True

