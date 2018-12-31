# validated: 2017-10-03 EN e1195e8b9dab edu/wpi/first/wpilibj/command/WaitCommand.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2016. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Optional

from .timedcommand import TimedCommand

__all__ = ["WaitCommand"]


class WaitCommand(TimedCommand):
    """A WaitCommand will wait for a certain amount of time before finishing.
    It is useful if you want a :class:`.CommandGroup` to pause for a moment.
    
    .. seealso:: :class:`.CommandGroup`
    """

    def __init__(self, timeout: float, name: Optional[str] = None) -> None:
        """Instantiates a WaitCommand with the given timeout.
        
        :param timeout: the time the command takes to run (seconds)
        :param name: the name of the command (optional)
        """
        if name is None:
            super().__init__("Wait(%s)" % timeout, timeout)
        else:
            super().__init__(name, timeout)
