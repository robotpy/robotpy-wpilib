#
# Everything in here should be usable on all implementations of the HAL
#

#############################################################################
# HAL
#############################################################################

kHALAllianceStationID_red1 = 0
kHALAllianceStationID_red2 = 1
kHALAllianceStationID_red3 = 2
kHALAllianceStationID_blue1 = 3
kHALAllianceStationID_blue2 = 4
kHALAllianceStationID_blue3 = 5

kMaxJoystickAxes = 12
kMaxJoystickPOVs = 12

class HALUsageReporting:
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
    kResourceType_TalonSRX = 51
    kResourceType_CANTalonSRX = 52

    # enum tInstances
    kLanguage_LabVIEW = 1
    kLanguage_CPlusPlus = 2
    kLanguage_Java = 3
    kLanguage_Python = 4

    kCANPlugin_BlackJagBridge = 1
    kCANPlugin_2CAN = 2

    kFramework_Iterative = 1
    kFramework_Simple = 2

    kRobotDrive_ArcadeStandard = 1
    kRobotDrive_ArcadeButtonSpin = 2
    kRobotDrive_ArcadeRatioCurve = 3
    kRobotDrive_Tank = 4
    kRobotDrive_MecanumPolar = 5
    kRobotDrive_MecanumCartesian = 6

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

#############################################################################
# Accelerometer
#############################################################################

class AccelerometerRange:
    kRange_2G = 0
    kRange_4G = 1
    kRange_8G = 2

#############################################################################
# Analog
#############################################################################

class AnalogTriggerType:
    kInWindow = 0
    kState = 1
    kRisingPulse = 2
    kFallingPulse = 3

#############################################################################
# Digital
#############################################################################

class Mode:
    kTwoPulse = 0
    kSemiperiod = 1
    kPulseLength = 2
    kExternalDirection = 3

#############################################################################
# TalonSRX
#############################################################################

class TalonSRXConst:
    kDefaultControlPeriodMs = 10

    # mode select enumerations
    kMode_DutyCycle = 0
    kMode_PositionCloseLoop = 1
    kMode_VelocityCloseLoop = 2
    kMode_CurrentCloseLoop = 3
    kMode_VoltCompen = 4
    kMode_SlaveFollower = 5
    kMode_NoDrive = 15

    # limit switch enumerations
    kLimitSwitchOverride_UseDefaultsFromFlash = 1
    kLimitSwitchOverride_DisableFwd_DisableRev = 4
    kLimitSwitchOverride_DisableFwd_EnableRev = 5
    kLimitSwitchOverride_EnableFwd_DisableRev = 6
    kLimitSwitchOverride_EnableFwd_EnableRev = 7

    # brake override enumerations
    kBrakeOverride_UseDefaultsFromFlash = 0
    kBrakeOverride_OverrideCoast = 1
    kBrakeOverride_OverrideBrake = 2

    # feedback device enumerations
    kFeedbackDev_DigitalQuadEnc = 0
    kFeedbackDev_AnalogPot = 2
    kFeedbackDev_AnalogEncoder = 3
    kFeedbackDev_CountEveryRisingEdge = 4
    kFeedbackDev_CountEveryFallingEdge = 5
    kFeedbackDev_PosIsPulseWidth = 8

    # ProfileSlotSelect enumerations
    kProfileSlotSelect_Slot0 = 0
    kProfileSlotSelect_Slot1 = 1

    # status frame rate types
    kStatusFrame_General = 0
    kStatusFrame_Feedback = 1
    kStatusFrame_Encoder = 2
    kStatusFrame_AnalogTempVbat = 3

class TalonSRXParam:
    # Signal enumeration for generic signal access
    eProfileParamSlot0_P = 1
    eProfileParamSlot0_I = 2
    eProfileParamSlot0_D = 3
    eProfileParamSlot0_F = 4
    eProfileParamSlot0_IZone = 5
    eProfileParamSlot0_CloseLoopRampRate = 6
    eProfileParamSlot1_P = 11
    eProfileParamSlot1_I = 12
    eProfileParamSlot1_D = 13
    eProfileParamSlot1_F = 14
    eProfileParamSlot1_IZone = 15
    eProfileParamSlot1_CloseLoopRampRate = 16
    eProfileParamSoftLimitForThreshold = 21
    eProfileParamSoftLimitRevThreshold = 22
    eProfileParamSoftLimitForEnable = 23
    eProfileParamSoftLimitRevEnable = 24
    eOnBoot_BrakeMode = 31
    eOnBoot_LimitSwitch_Forward_NormallyClosed = 32
    eOnBoot_LimitSwitch_Reverse_NormallyClosed = 33
    eOnBoot_LimitSwitch_Forward_Disable = 34
    eOnBoot_LimitSwitch_Reverse_Disable = 35
    eFault_OverTemp = 41
    eFault_UnderVoltage = 42
    eFault_ForLim = 43
    eFault_RevLim = 44
    eFault_HardwareFailure = 45
    eFault_ForSoftLim = 46
    eFault_RevSoftLim = 47
    eStckyFault_OverTemp = 48
    eStckyFault_UnderVoltage = 49
    eStckyFault_ForLim = 50
    eStckyFault_RevLim = 51
    eStckyFault_ForSoftLim = 52
    eStckyFault_RevSoftLim = 53
    eAppliedThrottle = 61
    eCloseLoopErr = 62
    eFeedbackDeviceSelect = 63
    eRevMotDuringCloseLoopEn = 64
    eModeSelect = 65
    eProfileSlotSelect = 66
    eRampThrottle = 67
    eRevFeedbackSensor = 68
    eLimitSwitchEn = 69
    eLimitSwitchClosedFor = 70
    eLimitSwitchClosedRev = 71
    eSensorPosition = 73
    eSensorVelocity = 74
    eCurrent = 75
    eBrakeIsEnabled = 76
    eEncPosition = 77
    eEncVel = 78
    eEncIndexRiseEvents = 79
    eQuadApin = 80
    eQuadBpin = 81
    eQuadIdxpin = 82
    eAnalogInWithOv = 83
    eAnalogInVel = 84
    eTemp = 85
    eBatteryV = 86
    eResetCount = 87
    eResetFlags = 88
    eFirmVers = 89
    eSettingsChanged = 90
    eQuadFilterEn = 91
    ePidIaccum = 93

TalonSRXParam_tostr = {getattr(TalonSRXParam, p): p for p in dir(TalonSRXParam) if not p.startswith('__')}

