# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/WaitUntilCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command

from ..timer import Timer

__all__ = ["WaitUntilCommand"]


class WaitUntilCommand(Command):
    """
    This will wait until the game clock reaches some value, then continue to
    the next command.
    """

    def __init__(self, time: float) -> None:
        super().__init__("WaitUntil(%s)" % time)
        self.time = time

    def isFinished(self) -> bool:
        # Check if we've reached the actual finish time.
        return Timer.getMatchTime() >= self.time
