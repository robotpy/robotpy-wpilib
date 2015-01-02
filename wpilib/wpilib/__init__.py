'''

    The WPI Robotics library (WPILib) is a set of classes that interfaces to the hardware in the FRC
    control system and your robot. There are classes to handle sensors, motors, the driver
    station, and a number of other utility functions like timing and field management.
    The library is designed to:
    
    - Deal with all the low level interfacing to these components so you can concentrate on
      solving this year's "robot problem". This is a philosophical decision to let you focus
      on the higher-level design of your robot rather than deal with the details of the
      processor and the operating system.
    - Understand everything at all levels by making the full source code of the library
      available. You can study (and modify) the algorithms used by the gyro class for
      oversampling and integration of the input signal or just ask the class for the current
      robot heading. You can work at any level.

'''

from .adxl345_i2c import *
from .adxl345_spi import *
from .analogaccelerometer import *
from .analoginput import *
from .analogoutput import *
from .analogpotentiometer import *
from .analogtrigger import *
from .analogtriggeroutput import *
from .builtinaccelerometer import *
from .canjaguar import *
from .cantalon import *
from .compressor import *
from .controllerpower import *
from .counter import *
from .digitalinput import *
from .digitaloutput import *
from .digitalsource import *
from .doublesolenoid import *
from .driverstation import *
from .encoder import *
from .geartooth import *
from .gyro import *
from .i2c import *
from .interruptablesensorbase import *
from .iterativerobot import *
from .jaguar import *
from .joystick import *
from .livewindow import *
from .livewindowsendable import *
from .motorsafety import *
from .pidcontroller import *
from .powerdistributionpanel import *
from .preferences import *
from .pwm import *
from .relay import *
from .resource import *
from .robotbase import *
from .robotdrive import *
from .robotstate import *
from .safepwm import *
from .samplerobot import *
from .sendable import *
from .sendablechooser import *
from .sensorbase import *
from .servo import *
from .smartdashboard import *
from .solenoidbase import *
from .solenoid import *
from .spi import *
from .talon import *
from .talonsrx import *
from .timer import *
from .ultrasonic import *
from .utility import *
from .victor import *
from .victorsp import *

# Provide dummy implementations if pynivision isn't available.
try:
    from .cameraserver import *
    from .usbcamera import *
except ImportError:
    from ._impl.dummycamera import *

from ._impl.main import run

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'
