# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/WaitForChildren.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

from .command import Command

__all__ = ["WaitForChildren"]


class WaitForChildren(Command):
    """This command will only finish if whatever :class:`.CommandGroup` it
    is in has no active children.  If it is not a part of a CommandGroup,
    then it will finish immediately.  If it is itself an active child, then
    the CommandGroup will never end.

    This class is useful for the situation where you want to allow anything
    running in parallel to finish, before continuing in the main CommandGroup
    sequence.
    """

    def isFinished(self) -> bool:
        return self.getGroup() is None or not self.getGroup().children
