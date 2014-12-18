"""
    Objects in this package allow you to implement a robot using Command-based
    programming.  Command based programming is a design pattern to help you
    organize your robot programs, by organizing your robot program into
    components based on :class:`.Command` and :class:`.Subsystem`
    
    The python implementation of the Command framework closely follows the 
    Java language implementation. RobotPy has several examples of command 
    based robots available.
    
    Each one of the objects in the Command framework has detailed
    documentation available. If you need more information, for examples,
    tutorials, and other detailed information on programming your robot
    using this pattern, we recommend that you consult the Java version of the
    `FRC Control System documentation <https://wpilib.screenstepslive.com/s/3120/m/7952/c/44956>`_
"""

from .command import *
from .commandgroup import *
from .pidcommand import *
from .pidsubsystem import *
from .printcommand import *
from .scheduler import *
from .startcommand import *
from .subsystem import *
from .waitcommand import *
from .waitforchildren import *
from .waituntilcommand import *
