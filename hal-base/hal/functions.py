import ctypes as C
import os as _os

from .exceptions import HALError
from .constants import *

from hal_impl.types import *
from hal_impl.fndef import *
from hal_impl import __hal_simulation__

def _STATUSFUNC(name, restype, *params, out=None, library=_dll,
                handle_missing=False):
    realparams = list(params)
    realparams.append(("status", C.POINTER(C.c_int32)))
    _inner = _RETFUNC(name, restype, *realparams, out=out, library=library,
                      handle_missing=handle_missing)
    def outer(*args, **kwargs):
        status = C.c_int32(0)
        rv = _inner(*args, status=status, **kwargs)
        if status.value != 0:
            raise HALError(getHALErrorMessage(status))
        return rv
    return outer

#############################################################################
# Semaphore
#############################################################################

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
                         ("mutex", MUTEX_ID), ("timeout", C.c_int32))
giveMultiWait = _RETFUNC("giveMultiWait", C.c_int8, ("sem", MULTIWAIT_ID))

#############################################################################
# HAL
#############################################################################

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
    errors = errors.encode('utf-8')
    return _HALSetErrorData(errors, len(errors), wait_ms)

HALGetControlWord = _RETFUNC("HALGetControlWord", C.c_int, ("data", HALControlWordPtr), out=["data"])

HALGetAllianceStation = _RETFUNC("HALGetAllianceStation", C.c_int, ("allianceStation", C.POINTER(C.c_int)), out=["allianceStation"])

_HALGetJoystickAxes = _RETFUNC("HALGetJoystickAxes", C.c_int, ("joystickNum", C.c_uint8), ("axes", HALJoystickAxes))
def HALGetJoystickAxes(joystickNum):
    axes = _HALJoystickAxes()
    _HALGetJoystickAxes(joystickNum, axes)
    return [x for x in axes.axes[0:axes.count]]

_HALGetJoystickPOVs = _RETFUNC("HALGetJoystickPOVs", C.c_int, ("joystickNum", C.c_uint8), ("povs", HALJoystickPOVs))
def HALGetJoystickPOVs(joystickNum):
    povs = _HALJoystickPOVs()
    _HALGetJoystickPOVs(joystickNum, povs)
    return [x for x in povs.povs[0:povs.count]]

_HALGetJoystickButtons = _RETFUNC("HALGetJoystickButtons", C.c_int, ("joystickNum", C.c_uint8), ("buttons", HALJoystickButtons))
def HALGetJoystickButtons(joystickNum):
    buttons = _HALJoystickButtons()
    _HALGetJoystickButtons(joystickNum, buttons)
    return buttons

_HALGetJoystickDescriptor = _RETFUNC("HALGetJoystickDescriptor", C.c_int, ("joystickNum", C.c_uint8), ("descriptor", HALJoystickDescriptor))
def HALGetJoystickDescriptor(joystickNum):
    descriptor = _HALJoystickDescriptor()
    _HALGetJoystickDescriptor(joystickNum, descriptor)
    return descriptor


HALSetJoystickOutputs = _RETFUNC("HALSetJoystickOutputs", C.c_int, ("joystickNum", C.c_uint8), ("outputs", C.c_uint32), ("leftRumble", C.c_uint16), ("rightRumble", C.c_uint16))

HALGetMatchTime = _RETFUNC("HALGetMatchTime", C.c_int, ("matchTime", C.POINTER(C.c_float)), out=["matchTime"])

HALSetNewDataSem = _RETFUNC("HALSetNewDataSem", None, ("sem", MULTIWAIT_ID))

HALGetSystemActive = _STATUSFUNC("HALGetSystemActive", C.c_bool)
HALGetBrownedOut = _STATUSFUNC("HALGetBrownedOut", C.c_bool)

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

_HALReport = _RETFUNC("HALReport", C.c_uint32, ("resource", C.c_uint8), ("instanceNumber", C.c_uint8), ("context", C.c_uint8, 0), ("feature", C.c_char_p, None))
def HALReport(resource, instanceNumber, context = 0, feature = None):
    if feature is not None:
        feature = feature.encode('utf-8')
    return _HALReport(resource, instanceNumber, context, feature)

def HALIsSimulation():
    return __hal_simulation__

#############################################################################
# Accelerometer
#############################################################################

setAccelerometerActive = _RETFUNC("setAccelerometerActive", None, ("active", C.c_bool))
setAccelerometerRange = _RETFUNC("setAccelerometerRange", None, ("range", C.c_int))
getAccelerometerX = _RETFUNC("getAccelerometerX", C.c_double)
getAccelerometerY = _RETFUNC("getAccelerometerY", C.c_double)
getAccelerometerZ = _RETFUNC("getAccelerometerZ", C.c_double)

#############################################################################
# Analog
#############################################################################

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
setAccumulatorCenter = _STATUSFUNC("setAccumulatorCenter", None, ("analog_port", AnalogPort), ('center', C.c_int32))
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
        raise IOError(_os.strerror(C.get_errno()))
    return [x for x in recv_buffer]

_spiWrite = _RETFUNC("spiWrite", C.c_int32, ("port", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
def spiWrite(port, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _spiWrite(port, buffer, send_size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))

_spiRead = _RETFUNC("spiRead", C.c_int32, ("port", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
def spiRead(port, count):
    buffer = C.c_uint8 * count
    rv = _spiRead(port, buffer, count)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
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
        raise IOError(_os.strerror(C.get_errno()))
    return [x for x in recv_buffer]

_i2CWrite = _RETFUNC("i2CWrite", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
def i2CWrite(port, device_address, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _i2CWrite(port, device_address, buffer, send_size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))

_i2CRead = _RETFUNC("i2CRead", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
def i2CRead(port, device_address, count):
    buffer = C.c_uint8 * count
    rv = _i2CRead(port, device_address, buffer, count)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return [x for x in buffer]

i2CClose = _RETFUNC("i2CClose", None, ("port", C.c_uint8))

#############################################################################
# Interrupts
#############################################################################

_InterruptHandlerFunction = C.CFUNCTYPE(None, C.c_uint32, C.c_void_p)
_interruptHandlers = {}

initializeInterrupts = _STATUSFUNC("initializeInterrupts", Interrupt, ("interrupt_index", C.c_uint32), ("watcher", C.c_bool))
_cleanInterrupts = _STATUSFUNC("cleanInterrupts", None, ("interrupt", Interrupt))
def cleanInterrupts(interrupt):
    _cleanInterrupts(interrupt)

    # remove references to function handlers
    _interruptHandlers.pop(interrupt, None)

waitForInterrupt = _STATUSFUNC("waitForInterrupt", C.c_uint32, ("interrupt", Interrupt), ("timeout", C.c_double), ("ignorePrevious", C.c_bool))
enableInterrupts = _STATUSFUNC("enableInterrupts", None, ("interrupt", Interrupt))
disableInterrupts = _STATUSFUNC("disableInterrupts", None, ("interrupt", Interrupt))
readRisingTimestamp = _STATUSFUNC("readRisingTimestamp", C.c_double, ("interrupt", Interrupt))
readFallingTimestamp = _STATUSFUNC("readFallingTimestamp", C.c_double, ("interrupt", Interrupt))
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
getPDPTotalCurrent = _STATUSFUNC("getPDPTotalCurrent", C.c_double)
getPDPTotalPower = _STATUSFUNC("getPDPTotalPower", C.c_double)
getPDPTotalEnergy = _STATUSFUNC("getPDPTotalEnergy", C.c_double)
resetPDPTotalEnergy = _STATUSFUNC("resetPDPTotalEnergy", None)
clearPDPStickyFaults = _STATUSFUNC("clearPDPStickyFaults", None)

#############################################################################
# Power
#############################################################################
getVinVoltage = _STATUSFUNC("getVinVoltage", C.c_float)
getVinCurrent = _STATUSFUNC("getVinCurrent", C.c_float)
getUserVoltage6V = _STATUSFUNC("getUserVoltage6V", C.c_float)
getUserCurrent6V = _STATUSFUNC("getUserCurrent6V", C.c_float)
getUserActive6V = _STATUSFUNC("getUserActive6V", C.c_bool)
getUserCurrentFaults6V = _STATUSFUNC("getUserCurrentFaults6V", C.c_int)
getUserVoltage5V = _STATUSFUNC("getUserVoltage5V", C.c_float)
getUserCurrent5V = _STATUSFUNC("getUserCurrent5V", C.c_float)
getUserActive5V = _STATUSFUNC("getUserActive5V", C.c_bool)
getUserCurrentFaults5V = _STATUSFUNC("getUserCurrentFaults5V", C.c_int)
getUserVoltage3V3 = _STATUSFUNC("getUserVoltage3V3", C.c_float)
getUserCurrent3V3 = _STATUSFUNC("getUserCurrent3V3", C.c_float)
getUserActive3V3 = _STATUSFUNC("getUserActive3V3", C.c_bool)
getUserCurrentFaults3V3 = _STATUSFUNC("getUserCurrentFaults3V3", C.c_int)

#############################################################################
# Solenoid
#############################################################################

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
