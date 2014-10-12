import ctypes as C
import os

_dll = C.CDLL("./libHALAthena_shared.so", use_errno=True)

class HALError(RuntimeError):
    pass

def _RETFUNC(name, restype, *params, out=None, library=_dll,
             errcheck=None, handle_missing=False):
    prototype = C.CFUNCTYPE(restype, *tuple(param[1] for param in params))
    paramflags = []
    for param in params:
        if out is not None and param[0] in out:
            dir = 2
        else:
            dir = 1
        if len(param) == 3:
            paramflags.append((dir, param[0], param[2]))
        else:
            paramflags.append((dir, param[0]))
    try:
        func = prototype((name, library), tuple(paramflags))
        if errcheck is not None:
            func.errcheck = errcheck
    except AttributeError:
        if not handle_missing:
            raise
        def func(*args, **kwargs):
            raise NotImplementedError
    return func

def _STATUSFUNC(name, restype, *params, out=None, library=_dll,
                handle_missing=False):
    realparams = list(params)
    realparams.append(("status", C.POINTER(C.c_int32)))
    _inner = _RETFUNC(name, restype, *realparams, out=out, library=library,
                      handle_missing=handle_missing)
    def outer(*args, **kwargs):
        status = C.c_int32(0)
        rv = _inner(*args, status=C.byref(status), **kwargs)
        if status.value != 0:
            raise HALError(getHALErrorMessage(status))
        return rv
    return outer

def _VAR(name, type, library=_dll):
    return type.in_dll(library, name)

#############################################################################
# Semaphore
#############################################################################

# pthread opaque structures
class _pthread_mutex_t(C.Structure):
    pass
MUTEX_ID = C.POINTER(_pthread_mutex_t)

class _sem_t(C.Structure):
    pass
SEMAPHORE_ID = C.POINTER(_sem_t)

class _pthread_cond_t(C.Structure):
    pass
MULTIWAIT_ID = C.POINTER(_pthread_cond_t)

SEMAPHORE_Q_FIFO = _VAR("SEMAPHORE_Q_FIFO", C.c_uint32)
SEMAPHORE_Q_PRIORITY = _VAR("SEMAPHORE_Q_PRIORITY", C.c_uint32)
SEMAPHORE_DELETE_SAFE = _VAR("SEMAPHORE_DELETE_SAFE", C.c_uint32)
SEMAPHORE_INVERSION_SAFE = _VAR("SEMAPHORE_INVERSION_SAFE", C.c_uint32)

SEMAPHORE_NO_WAIT = _VAR("SEMAPHORE_NO_WAIT", C.c_int32)
SEMAPHORE_WAIT_FOREVER = _VAR("SEMAPHORE_WAIT_FOREVER", C.c_int32)

SEMAPHORE_EMPTY = _VAR("SEMAPHORE_EMPTY", C.c_uint32)
SEMAPHORE_FULL = _VAR("SEMAPHORE_FULL", C.c_uint32)

initializeMutexRecursive = _RETFUNC("initializeMutexRecursive", MUTEX_ID)
initializeMutexNormal = _RETFUNC("initializeMutexNormal", MUTEX_ID)
deleteMutex = _RETFUNC("deleteMutex", None, ("sem", MUTEX_ID))
takeMutex = _RETFUNC("takeMutex", C.c_int8, ("sem", MUTEX_ID))
tryTakeMutex = _RETFUNC("tryTakeMutex", C.c_int8, ("sem", MUTEX_ID))
giveMutex = _RETFUNC("giveMutex", C.c_int8, ("sem", MUTEX_ID))

initializeSemaphore = _RETFUNC("initializeSemaphore", SEMAPHORE_ID,
                               ("initial_value", C.c_uint32))
deleteSemaphore = _RETFUNC("deleteSemaphore", None, ("sem", SEMAPHORE_ID))
takeSemaphore = _RETFUNC("takeSemaphore", C.c_int8, ("sem", SEMAPHORE_ID))
tryTakeSemaphore = _RETFUNC("tryTakeSemaphore", C.c_int8, ("sem", SEMAPHORE_ID))
giveSemaphore = _RETFUNC("giveSemaphore", C.c_int8, ("sem", SEMAPHORE_ID))

initializeMultiWait = _RETFUNC("initializeMultiWait", MULTIWAIT_ID)
deleteMultiWait = _RETFUNC("deleteMultiWait", None, ("sem", MULTIWAIT_ID))
takeMultiWait = _RETFUNC("takeMultiWait", C.c_int8, ("sem", MULTIWAIT_ID),
                         ("timeout", C.c_int32))
giveMultiWait = _RETFUNC("giveMultiWait", C.c_int8, ("sem", MULTIWAIT_ID))

#############################################################################
# HAL
#############################################################################

# opaque port structure
class _Port(C.Structure):
    pass
Port = C.POINTER(_Port)

class HALControlWord(C.Structure):
    _fields_ = [("enabled", C.c_uint32, 1),
                ("autonomous", C.c_uint32, 1),
                ("test", C.c_uint32, 1),
                ("eStop", C.c_uint32, 1),
                ("fmsAttached", C.c_uint32, 1),
                ("dsAttached", C.c_uint32, 1),
                ("control_reserved", C.c_uint32, 26)]

getPort = _RETFUNC("getPort", Port, ("pin", C.c_uint8))
getPortWithModule = _RETFUNC("getPortWithModule", Port, ("module", C.c_uint8), ("pin", C.c_uint8))
_getHALErrorMessage = _RETFUNC("getHALErrorMessage", C.c_char_p, ("code", C.c_int32))
def getHALErrorMessage(code):
    return _getHALErrorMessage(code).decode('utf_8')
getFPGAVersion = _STATUSFUNC("getFPGAVersion", C.c_uint16)
getFPGARevision = _STATUSFUNC("getFPGARevision", C.c_uint32)
getFPGATime = _STATUSFUNC("getFPGATime", C.c_uint32)

getFPGAButton = _STATUSFUNC("getFPGAButton", C.c_bool)

_HALSetErrorData = _RETFUNC("HALSetErrorData", C.c_int, ("errors", C.c_char_p), ("errorsLength", C.c_int), ("wait_ms", C.c_int))
def HALSetErrorData(errors, wait_ms):
    return _HALSetErrorData(errors, len(errors), wait_ms)

HALGetControlWord = _RETFUNC("HALGetControlWord", C.c_int, ("data", C.POINTER(HALControlWord)), out=["data"])

kHALAllianceStationID_red1 = 0
kHALAllianceStationID_red2 = 1
kHALAllianceStationID_red3 = 2
kHALAllianceStationID_blue1 = 3
kHALAllianceStationID_blue2 = 4
kHALAllianceStationID_blue3 = 5

HALGetAllianceStation = _RETFUNC("HALGetAllianceStation", C.c_int, ("allianceStation", C.POINTER(C.c_int)), out=["allianceStation"])

class _HALJoystickAxes(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("axes", C.c_int16 * 6)]

_HALGetJoystickAxes = _RETFUNC("HALGetJoystickAxes", C.c_int, ("joystickNum", C.c_uint8), ("axes", C.POINTER(_HALJoystickAxes)), ("maxAxes", C.c_uint8))
def HALGetJoystickAxes(joystickNum):
    axes = _HALJoystickAxes()
    _HALGetJoystickAxes(joystickNum, C.byref(axes), 6)
    return [x for x in axes.axes[0:axes.count]]

_HALGetJoystickButtons = _RETFUNC("HALGetJoystickButtons", C.c_int, ("joystickNum", C.c_uint8), ("buttons", C.POINTER(C.c_uint32)), ("count", C.POINTER(C.c_uint8)))
def HALGetJoystickButtons(joystickNum):
    buttons = C.c_uint32(0)
    count = C.c_uint8(0)
    _HALGetJoystickButtons(joystickNum, C.byref(buttons),
                           C.byref(count))
    return buttons.value

HALSetNewDataSem = _RETFUNC("HALSetNewDataSem", None, ("sem", MUTEX_ID))

_HALInitialize = _RETFUNC("HALInitialize", C.c_int, ("mode", C.c_int, 0))
def HALInitialize(mode = 0):
    rv = _HALInitialize(mode)
    if not rv:
        raise HALError("Could not initialize HAL")

HALNetworkCommunicationObserveUserProgramStarting = _RETFUNC("HALNetworkCommunicationObserveUserProgramStarting", None)
HALNetworkCommunicationObserveUserProgramDisabled = _RETFUNC("HALNetworkCommunicationObserveUserProgramDisabled", None)
HALNetworkCommunicationObserveUserProgramAutonomous = _RETFUNC("HALNetworkCommunicationObserveUserProgramAutonomous", None)
HALNetworkCommunicationObserveUserProgramTeleop = _RETFUNC("HALNetworkCommunicationObserveUserProgramTeleop", None)
HALNetworkCommunicationObserveUserProgramTest = _RETFUNC("HALNetworkCommunicationObserveUserProgramTest", None)

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

_HALReport = _RETFUNC("HALReport", C.c_uint32, ("resource", C.c_uint8), ("instanceNumber", C.c_uint8), ("context", C.c_uint8, 0), ("feature", C.c_char_p, None))
def HALReport(resource, instanceNumber, context = 0, feature = None):
    if feature is not None:
        feature = feature.encode('utf-8')
    return _HALReport(resource, instanceNumber, context, feature)

#############################################################################
# Accelerometer
#############################################################################
class AccelerometerRange:
    kRange_2G = 0
    kRange_4G = 1
    kRange_8G = 2

setAccelerometerActive = _RETFUNC("setAccelerometerActive", None, ("active", C.c_bool))
setAccelerometerRange = _RETFUNC("setAccelerometerRange", None, ("range", C.c_int))
getAccelerometerX = _RETFUNC("getAccelerometerX", C.c_double)
getAccelerometerY = _RETFUNC("getAccelerometerY", C.c_double)
getAccelerometerZ = _RETFUNC("getAccelerometerZ", C.c_double)

#############################################################################
# Analog
#############################################################################
class AnalogTriggerType:
    kInWindow = 0
    kState = 1
    kRisingPulse = 2
    kFallingPulse = 3

# opaque analog port
class _AnalogPort(C.Structure):
    pass
AnalogPort = C.POINTER(_AnalogPort)

# opaque analog trigger
class _AnalogTrigger(C.Structure):
    pass
AnalogTrigger = C.POINTER(_AnalogTrigger)

# Analog output functions
initializeAnalogOutputPort = _STATUSFUNC("initializeAnalogOutputPort", AnalogPort, ("port", Port))
setAnalogOutput = _STATUSFUNC("setAnalogOutput", None, ("analog_port", AnalogPort), ("voltage", C.c_double))
getAnalogOutput = _STATUSFUNC("getAnalogOutput", C.c_double, ("analog_port", AnalogPort))
checkAnalogOutputChannel = _RETFUNC("checkAnalogOutputChannel", C.c_bool, ("pin", C.c_uint32))

# Analog input functions
initializeAnalogInputPort = _STATUSFUNC("initializeAnalogInputPort", AnalogPort, ("port", Port))
checkAnalogModule = _RETFUNC("checkAnalogModule", C.c_bool, ("module", C.c_uint8))
checkAnalogInputChannel = _RETFUNC("checkAnalogInputChannel", C.c_bool, ("pin", C.c_uint32))

setAnalogSampleRate = _STATUSFUNC("setAnalogSampleRate", None, ("samples_per_second", C.c_double))
getAnalogSampleRate = _STATUSFUNC("getAnalogSampleRate", C.c_float)
setAnalogAverageBits = _STATUSFUNC("setAnalogAverageBits", None, ("analog_port", AnalogPort), ("bits", C.c_uint32))
getAnalogAverageBits = _STATUSFUNC("getAnalogAverageBits", C.c_uint32, ("analog_port", AnalogPort))
setAnalogOversampleBits = _STATUSFUNC("setAnalogOversampleBits", None, ("analog_port", AnalogPort), ("bits", C.c_uint32))
getAnalogOversampleBits = _STATUSFUNC("getAnalogOversampleBits", C.c_uint32, ("analog_port", AnalogPort))
getAnalogValue = _STATUSFUNC("getAnalogValue", C.c_int16, ("analog_port", AnalogPort))
getAnalogAverageValue = _STATUSFUNC("getAnalogAverageValue", C.c_int32, ("analog_port", AnalogPort))
getAnalogVoltsToValue = _STATUSFUNC("getAnalogVoltsToValue", C.c_int32, ("analog_port", AnalogPort), ("voltage", C.c_double))
getAnalogVoltage = _STATUSFUNC("getAnalogVoltage", C.c_float, ("analog_port", AnalogPort))
getAnalogAverageVoltage = _STATUSFUNC("getAnalogAverageVoltage", C.c_float, ("analog_port", AnalogPort))
getAnalogLSBWeight = _STATUSFUNC("getAnalogLSBWeight", C.c_uint32, ("analog_port", AnalogPort))
getAnalogOffset = _STATUSFUNC("getAnalogOffset", C.c_int32, ("analog_port", AnalogPort))

isAccumulatorChannel = _STATUSFUNC("isAccumulatorChannel", C.c_bool, ("analog_port", AnalogPort))
initAccumulator = _STATUSFUNC("initAccumulator", None, ("analog_port", AnalogPort))
resetAccumulator = _STATUSFUNC("resetAccumulator", None, ("analog_port", AnalogPort))
setAccumulatorCenter = _STATUSFUNC("setAccumulatorCenter", None, ("analog_port", AnalogPort))
setAccumulatorDeadband = _STATUSFUNC("setAccumulatorDeadband", None, ("analog_port", AnalogPort), ("deadband", C.c_int32))
getAccumulatorValue = _STATUSFUNC("getAccumulatorValue", C.c_int64, ("analog_port", AnalogPort))
getAccumulatorCount = _STATUSFUNC("getAccumulatorCount", C.c_uint32, ("analog_port", AnalogPort))
getAccumulatorOutput = _STATUSFUNC("getAccumulatorOutput", None, ("analog_port", AnalogPort), ("value", C.POINTER(C.c_int64)), ("count", C.POINTER(C.c_uint32)), out=["value", "count"])

initializeAnalogTrigger = _STATUSFUNC("initializeAnalogTrigger", AnalogTrigger, ("port", Port), ("index", C.POINTER(C.c_uint32)), out=["index"])
cleanAnalogTrigger = _STATUSFUNC("cleanAnalogTrigger", None, ("analog_trigger", AnalogTrigger))
setAnalogTriggerLimitsRaw = _STATUSFUNC("setAnalogTriggerLimitsRaw", None, ("analog_trigger", AnalogTrigger), ("lower", C.c_int32), ("upper", C.c_int32))
setAnalogTriggerLimitsVoltage = _STATUSFUNC("setAnalogTriggerLimitsVoltage", None, ("analog_trigger", AnalogTrigger), ("lower", C.c_double), ("upper", C.c_double))
setAnalogTriggerAveraged = _STATUSFUNC("setAnalogTriggerAveraged", None, ("analog_trigger", AnalogTrigger), ("use_averaged_value", C.c_bool))
setAnalogTriggerFiltered = _STATUSFUNC("setAnalogTriggerFiltered", None, ("analog_trigger", AnalogTrigger), ("use_filtered_value", C.c_bool))
getAnalogTriggerInWindow = _STATUSFUNC("getAnalogTriggerInWindow", C.c_bool, ("analog_trigger", AnalogTrigger))
getAnalogTriggerTriggerState = _STATUSFUNC("getAnalogTriggerTriggerState", C.c_bool, ("analog_trigger", AnalogTrigger))
getAnalogTriggerOutput = _STATUSFUNC("getAnalogTriggerOutput", C.c_bool, ("analog_trigger", AnalogTrigger), ("type", C.c_int))

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class _PCM(C.Structure):
    pass
PCM = C.POINTER(_PCM)

initializeCompressor = _RETFUNC("initializeCompressor", PCM, ("module", C.c_uint8))
checkCompressorModule = _RETFUNC("checkCompressorModule", C.c_bool, ("module", C.c_uint8))

getCompressor = _STATUSFUNC("getCompressor", C.c_bool, ("pcm", PCM))

setClosedLoopControl = _STATUSFUNC("setClosedLoopControl", None, ("pcm", PCM), ("value", C.c_bool))
getClosedLoopControl = _STATUSFUNC("getClosedLoopControl", C.c_bool, ("pcm", PCM))

getPressureSwitch = _STATUSFUNC("getPressureSwitch", C.c_bool, ("pcm", PCM))
getCompressorCurrent = _STATUSFUNC("getCompressorCurrent", C.c_float, ("pcm", PCM))

#############################################################################
# Digital
#############################################################################
class Mode:
    kTwoPulse = 0
    kSemiperiod = 1
    kPulseLength = 2
    kExternalDirection = 3

# opaque digital port
class _DigitalPort(C.Structure):
    pass
DigitalPort = C.POINTER(_DigitalPort)

# opaque PWM
class _PWM(C.Structure):
    pass
PWM = C.POINTER(_PWM)

# opaque counter
class _Counter(C.Structure):
    pass
Counter = C.POINTER(_Counter)

# opaque encoder
class _Encoder(C.Structure):
    pass
Encoder = C.POINTER(_Encoder)

initializeDigitalPort = _STATUSFUNC("initializeDigitalPort", DigitalPort, ("port", Port))
checkPWMChannel = _RETFUNC("checkPWMChannel", C.c_bool, ("digital_port", DigitalPort))
checkRelayChannel = _RETFUNC("checkRelayChannel", C.c_bool, ("digital_port", DigitalPort))

setPWM = _STATUSFUNC("setPWM", None, ("digital_port", DigitalPort), ("value", C.c_ushort))
allocatePWMChannel = _STATUSFUNC("allocatePWMChannel", C.c_bool, ("digital_port", DigitalPort))
freePWMChannel = _STATUSFUNC("freePWMChannel", None, ("digital_port", DigitalPort))
getPWM = _STATUSFUNC("getPWM", C.c_ushort, ("digital_port", DigitalPort))
latchPWMZero = _STATUSFUNC("latchPWMZero", None, ("digital_port", DigitalPort))
setPWMPeriodScale = _STATUSFUNC("setPWMPeriodScale", None, ("digital_port", DigitalPort), ("squelch_mask", C.c_uint32))
allocatePWM = _STATUSFUNC("allocatePWM", PWM)
freePWM = _STATUSFUNC("freePWM", None, ("pwm", PWM))
setPWMRate = _STATUSFUNC("setPWMRate", None, ("rate", C.c_double))
setPWMDutyCycle = _STATUSFUNC("setPWMDutyCycle", None, ("pwm", PWM), ("duty_cycle", C.c_double))
setPWMOutputChannel = _STATUSFUNC("setPWMOutputChannel", None, ("pwm", PWM), ("pin", C.c_uint32))

setRelayForward = _STATUSFUNC("setRelayForward", None, ("digital_port", DigitalPort), ("on", C.c_bool))
setRelayReverse = _STATUSFUNC("setRelayReverse", None, ("digital_port", DigitalPort), ("on", C.c_bool))
getRelayForward = _STATUSFUNC("getRelayForward", C.c_bool, ("digital_port", DigitalPort))
getRelayReverse = _STATUSFUNC("getRelayReverse", C.c_bool, ("digital_port", DigitalPort))

allocateDIO = _STATUSFUNC("allocateDIO", C.c_bool, ("digital_port", DigitalPort), ("input", C.c_bool))
freeDIO = _STATUSFUNC("freeDIO", None, ("digital_port", DigitalPort))
setDIO = _STATUSFUNC("setDIO", None, ("digital_port", DigitalPort), ("value", C.c_short))
getDIO = _STATUSFUNC("getDIO", C.c_bool, ("digital_port", DigitalPort))
getDIODirection = _STATUSFUNC("getDIODirection", C.c_bool, ("digital_port", DigitalPort))
pulse = _STATUSFUNC("pulse", None, ("digital_port", DigitalPort), ("pulse_length", C.c_double))
isPulsing = _STATUSFUNC("isPulsing", C.c_bool, ("digital_port", DigitalPort))
isAnyPulsing = _STATUSFUNC("isAnyPulsing", C.c_bool)

initializeCounter = _STATUSFUNC("initializeCounter", Counter, ("mode", C.c_int), ("index", C.POINTER(C.c_uint32)), out=["index"])
freeCounter = _STATUSFUNC("freeCounter", None, ("counter", Counter))
setCounterAverageSize = _STATUSFUNC("setCounterAverageSize", None, ("counter", Counter), ("size", C.c_int32))
setCounterUpSource = _STATUSFUNC("setCounterUpSource", None, ("counter", Counter), ("pin", C.c_uint32), ("analog_trigger", C.c_bool))
setCounterUpSourceEdge = _STATUSFUNC("setCounterUpSourceEdge", None, ("counter", Counter), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterUpSource = _STATUSFUNC("clearCounterUpSource", None, ("counter", Counter))
setCounterDownSource = _STATUSFUNC("setCounterDownSource", None, ("counter", Counter), ("pin", C.c_uint32), ("analog_trigger", C.c_bool))
setCounterDownSourceEdge = _STATUSFUNC("setCounterDownSourceEdge", None, ("counter", Counter), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterDownSource = _STATUSFUNC("clearCounterDownSource", None, ("counter", Counter))
setCounterUpDownMode = _STATUSFUNC("setCounterUpDownMode", None, ("counter", Counter))
setCounterExternalDirectionMode = _STATUSFUNC("setCounterExternalDirectionMode", None, ("counter", Counter))
setCounterSemiPeriodMode = _STATUSFUNC("setCounterSemiPeriodMode", None, ("counter", Counter), ("high_semi_period", C.c_bool))
setCounterPulseLengthMode = _STATUSFUNC("setCounterPulseLengthMode", None, ("counter", Counter), ("threshold", C.c_double))
getCounterSamplesToAverage = _STATUSFUNC("getCounterSamplesToAverage", C.c_int32, ("counter", Counter))
setCounterSamplesToAverage = _STATUSFUNC("setCounterSamplesToAverage", None, ("counter", Counter), ("samples_to_average", C.c_int))
startCounter = _STATUSFUNC("startCounter", None, ("counter", Counter))
stopCounter = _STATUSFUNC("stopCounter", None, ("counter", Counter))
resetCounter = _STATUSFUNC("resetCounter", None, ("counter", Counter))
getCounter = _STATUSFUNC("getCounter", C.c_int32, ("counter", Counter))
getCounterPeriod = _STATUSFUNC("getCounterPeriod", C.c_double, ("counter", Counter))
setCounterMaxPeriod = _STATUSFUNC("setCounterMaxPeriod", None, ("counter", Counter), ("max_period", C.c_double))
setCounterUpdateWhenEmpty = _STATUSFUNC("setCounterUpdateWhenEmpty", None, ("counter", Counter), ("enabled", C.c_bool))
getCounterStopped = _STATUSFUNC("getCounterStopped", C.c_bool, ("counter", Counter))
getCounterDirection = _STATUSFUNC("getCounterDirection", C.c_bool, ("counter", Counter))
setCounterReverseDirection = _STATUSFUNC("setCounterReverseDirection", None, ("counter", Counter), ("reverse_direction", C.c_bool))

initializeEncoder = _STATUSFUNC("initializeEncoder", Encoder,
        ("port_a_module", C.c_uint8), ("port_a_pin", C.c_uint32), ("port_a_analog_trigger", C.c_bool),
        ("port_b_module", C.c_uint8), ("port_b_pin", C.c_uint32), ("port_b_analog_trigger", C.c_bool),
        ("reverse_direction", C.c_bool), ("index", C.POINTER(C.c_int32)), out=["index"])
freeEncoder = _STATUSFUNC("freeEncoder", None, ("encoder", Encoder))
startEncoder = _STATUSFUNC("startEncoder", None, ("encoder", Encoder))
stopEncoder = _STATUSFUNC("stopEncoder", None, ("encoder", Encoder))
resetEncoder = _STATUSFUNC("resetEncoder", None, ("encoder", Encoder))
getEncoder = _STATUSFUNC("getEncoder", C.c_int32, ("encoder", Encoder))
getEncoderPeriod = _STATUSFUNC("getEncoderPeriod", C.c_double, ("encoder", Encoder))
setEncoderMaxPeriod = _STATUSFUNC("setEncoderMaxPeriod", None, ("encoder", Encoder), ("max_period", C.c_double))
getEncoderStopped = _STATUSFUNC("getEncoderStopped", C.c_bool, ("encoder", Encoder))
getEncoderDirection = _STATUSFUNC("getEncoderDirection", C.c_bool, ("encoder", Encoder))
setEncoderReverseDirection = _STATUSFUNC("setEncoderReverseDirection", None, ("encoder", Encoder), ("reverse_direction", C.c_bool))
setEncoderSamplesToAverage = _STATUSFUNC("setEncoderSamplesToAverage", None, ("encoder", Encoder), ("samples_to_average", C.c_uint32))
getEncoderSamplesToAverage = _STATUSFUNC("getEncoderSamplesToAverage", C.c_uint32, ("encoder", Encoder))

getLoopTiming = _STATUSFUNC("getLoopTiming", C.c_uint16)

spiInitialize = _STATUSFUNC("spiInitialize", None, ("port", C.c_uint8))

_spiTransaction = _RETFUNC("spiTransaction", C.c_int32, ("port", C.c_uint8),
                           ("data_to_send", C.POINTER(C.c_uint8)), ("data_received", C.POINTER(C.c_uint8)), ("size", C.c_uint8))
def spiTransaction(port, data_to_send):
    size = len(data_to_send)
    send_buffer = (C.c_uint8 * size)(*data_to_send)
    recv_buffer = C.c_uint8 * size
    rv = _spiTransaction(port, send_buffer, recv_buffer, size)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))
    return [x for x in recv_buffer]

_spiWrite = _RETFUNC("spiWrite", C.c_int32, ("port", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
def spiWrite(port, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _spiWrite(port, buffer, send_size)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))

_spiRead = _RETFUNC("spiRead", C.c_int32, ("port", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
def spiRead(port, count):
    buffer = C.c_uint8 * count
    rv = _spiRead(port, buffer, count)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))
    return [x for x in buffer]

spiClose = _RETFUNC("spiClose", None, ("port", C.c_uint8))
spiSetSpeed = _RETFUNC("spiSetSpeed", None, ("port", C.c_uint8), ("speed", C.c_uint32))
#spiSetBitsPerWord = _RETFUNC("spiSetBitsPerWord", None, ("port", C.c_uint8), ("bpw", C.c_uint8))
spiSetOpts = _RETFUNC("spiSetOpts", None, ("port", C.c_uint8), ("msb_first", C.c_int), ("sample_on_trailing", C.c_int), ("clk_idle_high", C.c_int))
spiSetChipSelectActiveHigh = _STATUSFUNC("spiSetChipSelectActiveHigh", None, ("port", C.c_uint8))
spiSetChipSelectActiveLow = _STATUSFUNC("spiSetChipSelectActiveLow", None, ("port", C.c_uint8))
spiGetHandle = _RETFUNC("spiGetHandle", C.c_int32, ("port", C.c_uint8));
spiSetHandle = _RETFUNC("spiSetHandle", None, ("port", C.c_uint8), ("handle", C.c_int32))
spiGetSemaphore = _RETFUNC("spiGetSemaphore", MUTEX_ID, ("port", C.c_uint8))
spiSetSemaphore = _RETFUNC("spiSetSemaphore", None, ("port", C.c_uint8), ("semaphore", MUTEX_ID))

i2CInitialize = _STATUSFUNC("i2CInitialize", None, ("port", C.c_uint8))

_i2CTransaction = _RETFUNC("i2CTransaction", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8),
                           ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8),
                           ("data_received", C.POINTER(C.c_uint8)), ("receive_size", C.c_uint8))
def i2CTransaction(port, device_address, data_to_send, receive_size):
    send_size = len(data_to_send)
    send_buffer = (C.c_uint8 * send_size)(*data_to_send)
    recv_buffer = C.c_uint8 * receive_size
    rv = _i2CTransaction(port, device_address, send_buffer, send_size, recv_buffer, receive_size)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))
    return [x for x in recv_buffer]

_i2CWrite = _RETFUNC("i2CWrite", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
def i2CWrite(port, device_address, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _i2CWrite(port, device_address, buffer, send_size)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))

_i2CRead = _RETFUNC("i2CRead", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
def i2CRead(port, device_address, count):
    buffer = C.c_uint8 * count
    rv = _i2CRead(port, device_address, buffer, count)
    if rv < 0:
        raise IOError(os.strerror(ctypes.get_errno()))
    return [x for x in buffer]

i2CClose = _RETFUNC("i2CClose", None, ("port", C.c_uint8))

#############################################################################
# Interrupts
#############################################################################

# opaque interrupt
class _Interrupt(C.Structure):
    pass
Interrupt = C.POINTER(_Interrupt)

_InterruptHandlerFunction = C.CFUNCTYPE(None, C.c_uint32, C.c_void_p)
_interruptHandlers = {}

initializeInterrupts = _STATUSFUNC("initializeInterrupts", Interrupt, ("interrupt_index", C.c_uint32), ("watcher", C.c_bool))
_cleanInterrupts = _STATUSFUNC("cleanInterrupts", None, ("interrupt", Interrupt))
def cleanInterrupts(interrupt):
    _cleanInterrupts(interrupt)

    # remove references to function handlers
    _interruptHandlers.pop(interrupt, None)

waitForInterrupt = _STATUSFUNC("waitForInterrupt", None, ("interrupt", Interrupt), ("timeout", C.c_double))
enableInterrupts = _STATUSFUNC("enableInterrupts", None, ("interrupt", Interrupt))
disableInterrupts = _STATUSFUNC("disableInterrupts", None, ("interrupt", Interrupt))
readInterruptTimestamp = _STATUSFUNC("readInterruptTimestamp", C.c_double, ("interrupt", Interrupt))
requestInterrupts = _STATUSFUNC("requestInterrupts", None, ("interrupt", Interrupt), ("routing_module", C.c_uint8), ("routing_pin", C.c_uint32), ("routing_analog_trigger", C.c_bool))
_attachInterruptHandler = _STATUSFUNC("attachInterruptHandler", None, ("interrupt", Interrupt), ("handler", _InterruptHandlerFunction), ("param", C.c_void_p))
def attachInterruptHandler(interrupt, handler):
    # While attachInterruptHandler provides a param parameter, we use ctypes
    # magic instead to uniquify the callback handler

    # create bounce function to drop param
    cb_func = _InterruptHandlerFunction(lambda mask, param: handler(mask))

    # keep reference to it
    handlers = _interruptHandlers.setdefault(interrupt, [])
    handlers.append(cb_func)

    # actually attach
    _attachInterruptHandler(interrupt, cb_func, None)

setInterruptUpSourceEdge = _STATUSFUNC("setInterruptUpSourceEdge", None, ("interrupt", Interrupt), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))

#############################################################################
# Notifier
#############################################################################

# opaque Notifier
class _Notifier(C.Structure):
    pass
Notifier = C.POINTER(_Notifier)

_NotifierProcessQueueFunction = C.CFUNCTYPE(None, C.c_uint32, C.c_void_p)
_notifierProcessQueueFunctions = {}

_initializeNotifier = _STATUSFUNC("initializeNotifier", Notifier, ("processQueue", _NotifierProcessQueueFunction))
def initializeNotifier(processQueue):
    # While initializeNotifier provides a param parameter, we use ctypes
    # magic instead to uniquify the callback handler

    # create bounce function to drop param
    cb_func = _NotifierProcessQueueFunction(lambda mask, param: processQueue(mask))

    # initialize notifier
    notifier = _attachInterruptHandler(interrupt, cb_func, None)

    # keep reference to bounce function
    handlers = _notifierProcessQueueFunctions[notifier] = cb_func

_cleanNotifier = _STATUSFUNC("cleanNotifier", None, ("notifier", Notifier))
def cleanNotifier(notifier):
    _cleanNotifier(notifier)

    # remove reference to process queue function
    _notifierProcessQueueFunctions.pop(notifier, None)

updateNotifierAlarm = _STATUSFUNC("updateNotifierAlarm", None, ("notifier", Notifier), ("triggerTime", C.c_uint32))

#############################################################################
# PDP
#############################################################################
getPDPTemperature = _STATUSFUNC("getPDPTemperature", C.c_double)
getPDPVoltage = _STATUSFUNC("getPDPVoltage", C.c_double)
getPDPChannelCurrent = _STATUSFUNC("getPDPChannelCurrent", C.c_double, ("channel", C.c_uint8))

#############################################################################
# Power
#############################################################################
getVinVoltage = _STATUSFUNC("getVinVoltage", C.c_float)
getVinCurrent = _STATUSFUNC("getVinCurrent", C.c_float)
getUserVoltage6V = _STATUSFUNC("getUserVoltage6V", C.c_float)
getUserCurrent6V = _STATUSFUNC("getUserCurrent6V", C.c_float)
getUserVoltage5V = _STATUSFUNC("getUserVoltage5V", C.c_float)
getUserCurrent5V = _STATUSFUNC("getUserCurrent5V", C.c_float)
getUserVoltage3V3 = _STATUSFUNC("getUserVoltage3V3", C.c_float)
getUserCurrent3V3 = _STATUSFUNC("getUserCurrent3V3", C.c_float)

#############################################################################
# Solenoid
#############################################################################

# opaque SolenoidPort
class _SolenoidPort(C.Structure):
    pass
SolenoidPort = C.POINTER(_SolenoidPort)

initializeSolenoidPort = _STATUSFUNC("initializeSolenoidPort", SolenoidPort, ("port", Port))
checkSolenoidModule = _RETFUNC("checkSolenoidModule", C.c_bool, ("module", C.c_uint8))

getSolenoid = _STATUSFUNC("getSolenoid", C.c_bool, ("solenoid_port", SolenoidPort))
setSolenoid = _STATUSFUNC("setSolenoid", None, ("solenoid_port", SolenoidPort), ("value", C.c_bool))

#############################################################################
# Utilities
#############################################################################
HAL_NO_WAIT = _VAR("HAL_NO_WAIT", C.c_int32)
HAL_WAIT_FOREVER = _VAR("HAL_WAIT_FOREVER", C.c_int32)

delayTicks = _RETFUNC("delayTicks", None, ("ticks", C.c_int32))
delayMillis = _RETFUNC("delayMillis", None, ("ms", C.c_double))
delaySeconds = _RETFUNC("delaySeconds", None, ("s", C.c_double))

