'''
    This is the core of WPILib.
'''

import importlib
import sys

from ._impl.main import run

try:
    from .version import __version__
except ImportError:
    __version__ = 'master'

__all__ = (
    'AccumulatorResult',
    'ADXL345_I2C',
    'ADXL345_SPI',
    'ADXL362',
    'ADXRS450_Gyro',
    'AnalogAccelerometer',
    'AnalogInput',
    'AnalogGyro',
    'AnalogOutput',
    'AnalogPotentiometer',
    'AnalogTrigger',
    'AnalogTriggerOutput',
    'BuiltInAccelerometer',
    'CameraServer',
    'Compressor',
    'ControllerPower',
    'Counter',
    'DigitalGlitchFilter',
    'DigitalInput',
    'DigitalOutput',
    'DigitalSource',
    'DMC60',
    'DoubleSolenoid',
    'DriverStation',
    'Encoder',
    'Filter',
    'GearTooth',
    'GyroBase',
    'I2C',
    'InterruptableSensorBase',
    'IterativeRobot',
    'IterativeRobotBase',
    'Jaguar',
    'Joystick',
    'LinearDigitalFilter',
    'LiveWindow',
    'LiveWindowSendable',
    'MotorSafety',
    'NidecBrushless',
    'Notifier',
    'PIDController',
    'PowerDistributionPanel',
    'Preferences',
    'PWM',
    'PWMSpeedController',
    'PWMTalonSRX',
    'PWMVictorSPX',
    'Relay',
    'Resource',
    'RobotBase',
    'RobotController',
    'RobotDrive',
    'RobotState',
    'SafePWM',
    'SampleRobot',
    'SD540',
    'Sendable',
    'SendableBase',
    'SendableBuilder',
    'SendableChooser',
    'SensorBase',
    'SerialPort',
    'Servo',
    'SmartDashboard',
    'SolenoidBase',
    'Solenoid',
    'Spark',
    'SpeedControllerGroup',
    'SPI',
    'Talon',
    'TimedRobot',
    'Timer',
    'Ultrasonic',
    'Utility',
    'Victor',
    'VictorSP',
    'XboxController',
)


class WPILibLazyLoader:
    # TODO: use module __getattr__ when we drop support for Python < 3.7

    # Re-export things that Python expects at module level that are rarely used.
    __doc__ = __doc__
    __all__ = __all__
    __file__ = __file__
    __loader__ = __loader__
    __spec__ = __spec__

    __version__ = __version__

    def __init__(self):
        self._impl = _impl  # noqa: F821
        self.run = run

        # Re-export things used by the Python import machinery.
        self.__name__ = __name__
        self.__package__ = __package__
        self.__path__ = __path__

    def __getattr__(self, name):
        if not name[0].isupper():
            raise AttributeError("module 'wpilib' has no attribute {!r}".format(name))
        mod = importlib.import_module('.' + name.lower(), 'wpilib')
        cls = getattr(mod, name)
        setattr(self, name, cls)
        return cls


sys.modules['wpilib'] = WPILibLazyLoader()
