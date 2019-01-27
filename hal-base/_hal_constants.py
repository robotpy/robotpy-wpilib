#
# Everything in here should be usable on all implementations of the HAL
#

import enum

#############################################################################
# HAL
#############################################################################


class RuntimeType(enum.IntEnum):
    Athena = 0
    Mock = 1


class UsageReporting:
    # enum tResourceType
    kResourceType_Controller = 0
    kResourceType_Module = 1
    kResourceType_Language = 2
    kResourceType_CANPlugin = 3
    kResourceType_Accelerometer = 4
    kResourceType_ADXL345 = 5
    kResourceType_AnalogChannel = 6
    kResourceType_AnalogTrigger = 7
    kResourceType_AnalogTriggerOutput = 8
    kResourceType_CANJaguar = 9
    kResourceType_Compressor = 10
    kResourceType_Counter = 11
    kResourceType_Dashboard = 12
    kResourceType_DigitalInput = 13
    kResourceType_DigitalOutput = 14
    kResourceType_DriverStationCIO = 15
    kResourceType_DriverStationEIO = 16
    kResourceType_DriverStationLCD = 17
    kResourceType_Encoder = 18
    kResourceType_GearTooth = 19
    kResourceType_Gyro = 20
    kResourceType_I2C = 21
    kResourceType_Framework = 22
    kResourceType_Jaguar = 23
    kResourceType_Joystick = 24
    kResourceType_Kinect = 25
    kResourceType_KinectStick = 26
    kResourceType_PIDController = 27
    kResourceType_Preferences = 28
    kResourceType_PWM = 29
    kResourceType_Relay = 30
    kResourceType_RobotDrive = 31
    kResourceType_SerialPort = 32
    kResourceType_Servo = 33
    kResourceType_Solenoid = 34
    kResourceType_SPI = 35
    kResourceType_Task = 36
    kResourceType_Ultrasonic = 37
    kResourceType_Victor = 38
    kResourceType_Button = 39
    kResourceType_Command = 40
    kResourceType_AxisCamera = 41
    kResourceType_PCVideoServer = 42
    kResourceType_SmartDashboard = 43
    kResourceType_Talon = 44
    kResourceType_HiTechnicColorSensor = 45
    kResourceType_HiTechnicAccel = 46
    kResourceType_HiTechnicCompass = 47
    kResourceType_SRF08 = 48
    kResourceType_AnalogOutput = 49
    kResourceType_VictorSP = 50
    kResourceType_PWMTalonSRX = 51
    kResourceType_CANTalonSRX = 52
    kResourceType_ADXL362 = 53
    kResourceType_ADXRS450 = 54
    kResourceType_RevSPARK = 55
    kResourceType_MindsensorsSD540 = 56
    kResourceType_DigitalGlitchFilter = 57
    kResourceType_ADIS16448 = 58
    kResourceType_PDP = 59
    kResourceType_PCM = 60
    kResourceType_PigeonIMU = 61
    kResourceType_NidecBrushless = 62
    kResourceType_CANifier = 63
    kResourceType_CTRE_future0 = 64
    kResourceType_CTRE_future1 = 65
    kResourceType_CTRE_future2 = 66
    kResourceType_CTRE_future3 = 67
    kResourceType_CTRE_future4 = 68
    kResourceType_CTRE_future5 = 69
    kResourceType_CTRE_future6 = 70
    kResourceType_LinearFilter = 71
    kResourceType_XboxController = 72
    kResourceType_UsbCamera = 73
    kResourceType_NavX = 74
    kResourceType_Pixy = 75
    kResourceType_Pixy2 = 76
    kResourceType_ScanseSweep = 77
    kResourceType_Shuffleboard = 78
    kResourceType_CAN = 79
    kResourceType_DigilentDMC60 = 80
    kResourceType_PWMVictorSPX = 81
    kResourceType_RevSparkMaxPWM = 82
    kResourceType_RevSparkMaxCAN = 83

    # enum tInstances
    kLanguage_LabVIEW = 1
    kLanguage_CPlusPlus = 2
    kLanguage_Java = 3
    kLanguage_Python = 4
    kLanguage_DotNet = 5

    kCANPlugin_BlackJagBridge = 1
    kCANPlugin_2CAN = 2

    kFramework_Iterative = 1
    kFramework_Sample = 2
    kFramework_CommandControl = 3
    kFramework_Timed = 4
    kFramework_ROS = 5
    kFramework_RobotBuilder = 6

    kRobotDrive_ArcadeStandard = 1
    kRobotDrive_ArcadeButtonSpin = 2
    kRobotDrive_ArcadeRatioCurve = 3
    kRobotDrive_Tank = 4
    kRobotDrive_MecanumPolar = 5
    kRobotDrive_MecanumCartesian = 6
    kRobotDrive2_DifferentialArcade = 7
    kRobotDrive2_DifferentialTank = 8
    kRobotDrive2_DifferentialCurvature = 9
    kRobotDrive2_MecanumCartesian = 10
    kRobotDrive2_MecanumPolar = 11
    kRobotDrive2_KilloughCartesian = 12
    kRobotDrive2_KilloughPolar = 13

    kDriverStationCIO_Analog = 1
    kDriverStationCIO_DigitalIn = 2
    kDriverStationCIO_DigitalOut = 3

    kDriverStationEIO_Acceleration = 1
    kDriverStationEIO_AnalogIn = 2
    kDriverStationEIO_AnalogOut = 3
    kDriverStationEIO_Button = 4
    kDriverStationEIO_LED = 5
    kDriverStationEIO_DigitalIn = 6
    kDriverStationEIO_DigitalOut = 7
    kDriverStationEIO_FixedDigitalOut = 8
    kDriverStationEIO_PWM = 9
    kDriverStationEIO_Encoder = 10
    kDriverStationEIO_TouchSlider = 11

    kADXL345_SPI = 1
    kADXL345_I2C = 2

    kCommand_Scheduler = 1

    kSmartDashboard_Instance = 1


HALUsageReporting = UsageReporting

#############################################################################
# Accelerometer.h
#############################################################################


class AccelerometerRange(enum.IntEnum):
    kRange_2G = 0
    kRange_4G = 1
    kRange_8G = 2


#############################################################################
# AnalogTrigger.h
#############################################################################


class AnalogTriggerType(enum.IntEnum):
    kInWindow = 0
    kState = 1
    kRisingPulse = 2
    kFallingPulse = 3


#############################################################################
# CANAPI.h
#############################################################################


class CANDeviceType(enum.IntEnum):
    kBroadcast = 0
    kRobotController = 1
    kMotorController = 2
    kRelayController = 3
    kGyroSensor = 4
    kAccelerometer = 5
    kUltrasonicSensor = 6
    kGearToothSensor = 7
    kPowerDistribution = 8
    kPneumatics = 9
    kMiscellaneous = 10
    kFirmwareUpdate = 31


class CANManufacturer(enum.IntEnum):
    kBroadcast = 0
    kNI = 1
    kLM = 2
    kDEKA = 3
    kCTRE = 4
    kMS = 7
    kTeamUse = 8


#############################################################################
# Counter.h
#############################################################################


class CounterMode(enum.IntEnum):
    kTwoPulse = 0
    kSemiperiod = 1
    kPulseLength = 2
    kExternalDirection = 3


#############################################################################
# DriverStation.h
#############################################################################


class AllianceStationID(enum.IntEnum):
    kRed1 = 0
    kRed2 = 1
    kRed3 = 2
    kBlue1 = 3
    kBlue2 = 4
    kBlue3 = 5


class MatchType(enum.IntEnum):
    kMatchType_none = 0
    kMatchType_practice = 1
    kMatchType_qualification = 2
    kMatchType_elimination = 3


kMaxJoystickAxes = 12
kMaxJoystickPOVs = 12

#############################################################################
# Encoder.h
#############################################################################


class EncoderIndexingType(enum.IntEnum):
    kResetWhileHigh = 0
    kResetWhileLow = 1
    kResetOnFallingEdge = 2
    kResetOnRisingEdge = 3


class EncoderEncodingType(enum.IntEnum):
    k1X = 0
    k2X = 1
    k4X = 2
