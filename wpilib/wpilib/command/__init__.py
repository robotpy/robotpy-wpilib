"""
    Objects in this package allow you to implement a robot using Command-based
    programming.  Command based programming is a design pattern to help you
    organize your robot programs, by organizing your robot program into
    components based on :class:`.Command` and :class:`.Subsystem`
    
    The Python implementation of the Command framework closely follows the
    Java language implementation. RobotPy has several examples of command
    based robots available.
    
    Each one of the objects in the Command framework has detailed
    documentation available. If you need more information, for examples,
    tutorials, and other detailed information on programming your robot
    using this pattern, we recommend that you consult the Java version of the
    `FRC Control System documentation <http://wpilib.screenstepslive.com/s/4485/m/13809/c/88893>`_
"""

from .command import Command
from .commandgroup import CommandGroup
from .conditionalcommand import ConditionalCommand
from .instantcommand import InstantCommand
from .pidcommand import PIDCommand
from .pidsubsystem import PIDSubsystem
from .printcommand import PrintCommand
from .scheduler import Scheduler
from .startcommand import StartCommand
from .subsystem import Subsystem
from .timedcommand import TimedCommand
from .waitcommand import WaitCommand
from .waitforchildren import WaitForChildren
from .waituntilcommand import WaitUntilCommand
