"""
    This package contains objects that can be used to determine the
    requirements of various interfaces used in WPILib. 
    
    Generally, the python version of WPILib does not require that you inherit
    from any of these interfaces, but instead will allow you to use custom 
    objects as long as they have the same methods.
"""

from .accelerometer import Accelerometer
from .controller import Controller
from .counterbase import CounterBase
from .generichid import GenericHID
from .gyro import Gyro
from .namedsendable import NamedSendable
from .pidoutput import PIDOutput
from .pidsource import PIDSource
from .potentiometer import Potentiometer
from .speedcontroller import SpeedController
