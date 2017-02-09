'''
    This is the core of WPILib.
'''

from .adxl345_i2c import *
from .adxl345_spi import *
from .adxl362 import *
from .adxrs450_gyro import *
from .analogaccelerometer import *
from .analoginput import *
from .analoggyro import *
from .analogoutput import *
from .analogpotentiometer import *
from .analogtrigger import *
from .analogtriggeroutput import *
from .builtinaccelerometer import *
from .cameraserver import *
from .canjaguar import *
from .cantalon import *
from .compressor import *
from .controllerpower import *
from .counter import *
from .digitalglitchfilter import *
from .digitalinput import *
from .digitaloutput import *
from .digitalsource import *
from .doublesolenoid import *
from .driverstation import *
from .encoder import *
from .filter import *
from .geartooth import *
from .gyrobase import *
from .i2c import *
from .interruptablesensorbase import *
from .iterativerobot import *
from .jaguar import *
from .joystick import *
from .lineardigitalfilter import *
from .livewindow import *
from .livewindowsendable import *
from .motorsafety import *
from .pidcontroller import *
from .powerdistributionpanel import *
from .preferences import *
from .pwm import *
from .pwmspeedcontroller import *
from .relay import *
from .resource import *
from .robotbase import *
from .robotdrive import *
from .robotstate import *
from .safepwm import *
from .samplerobot import *
from .sd540 import *
from .sendable import *
from .sendablechooser import *
from .sensorbase import *
from .servo import *
from .smartdashboard import *
from .solenoidbase import *
from .solenoid import *
from .spark import *
from .spi import *
from .talon import *
from .talonsrx import *
from .timer import *
from .ultrasonic import *
from .utility import *
from .victor import *
from .victorsp import *
from .xboxcontroller import *

from ._impl.main import run

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'
