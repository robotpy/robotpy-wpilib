import ctypes as C
import os as _os
import warnings

from .exceptions import HALError
from .constants import *

from hal_impl.types import *
from hal_impl.fndef import *
from hal_impl import __hal_simulation__

def hal_wrapper(f):
    '''Decorator to support introspection. The wrapped function must be
       the same name as the wrapper function, but start with an underscore
    '''
    
    wrapped = globals()['_' + f.__name__]
    if hasattr(f, 'fndata'):
        f.fndata = wrapped.fndata
    return f

def _STATUSFUNC(name, restype, *params, out=None, library=_dll,
                handle_missing=False):
    realparams = list(params)
    realparams.append(("status", C.POINTER(C.c_int32)))
    if restype is not None and out is not None:
        outindexes = [i for i, p in enumerate(params) if p[0] in out]
        def errcheck(rv, f, args):
            out = [rv]
            out.extend(args[i].value for i in outindexes)
            return tuple(out)
    else:
        errcheck = None
    _inner = _RETFUNC(name, restype, *realparams, out=out, library=library,
                      errcheck=errcheck, handle_missing=handle_missing)
    def outer(*args, **kwargs):
        status = C.c_int32(0)
        rv = _inner(*args, status=status, **kwargs)
        if status.value != 0:
            raise HALError(getHALErrorMessage(status.value))
        return rv
    
    # Support introspection for API validation
    if hasattr(_inner, 'fndata'):
        outer.fndata = _inner.fndata
    return outer

def _CTRFUNC_errcheck(result, func, args):
    if result != 0:
        warnings.warn(getHALErrorMessage(result))
    return args

def _CTRFUNC(name, *params, out=None, library=_dll, handle_missing=False):
    return _RETFUNC(name, C.c_int, *params, out=out, library=library,
                    handle_missing=handle_missing, errcheck=_CTRFUNC_errcheck)

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

getPort = _RETFUNC("getPort", Port_ptr, ("pin", C.c_uint8))
getPortWithModule = _RETFUNC("getPortWithModule", Port_ptr, ("module", C.c_uint8), ("pin", C.c_uint8))

_getHALErrorMessage = _RETFUNC("getHALErrorMessage", C.c_char_p, ("code", C.c_int32))
@hal_wrapper
def getHALErrorMessage(code):
    return _getHALErrorMessage(code).decode('utf_8')

getFPGAVersion = _STATUSFUNC("getFPGAVersion", C.c_uint16)
getFPGARevision = _STATUSFUNC("getFPGARevision", C.c_uint32)
getFPGATime = _STATUSFUNC("getFPGATime", C.c_uint32)

getFPGAButton = _STATUSFUNC("getFPGAButton", C.c_bool)

_HALSetErrorData = _RETFUNC("HALSetErrorData", C.c_int, ("errors", C.c_char_p), ("errorsLength", C.c_int), ("wait_ms", C.c_int))
@hal_wrapper
def HALSetErrorData(errors, wait_ms):
    errors = errors.encode('utf-8')
    return _HALSetErrorData(errors, len(errors), wait_ms)

HALGetControlWord = _RETFUNC("HALGetControlWord", C.c_int, ("data", HALControlWord_ptr), out=["data"])

HALGetAllianceStation = _RETFUNC("HALGetAllianceStation", C.c_int, ("allianceStation", C.POINTER(C.c_int)), out=["allianceStation"])

_HALGetJoystickAxes = _RETFUNC("HALGetJoystickAxes", C.c_int, ("joystickNum", C.c_uint8), ("axes", HALJoystickAxes_ptr))
@hal_wrapper
def HALGetJoystickAxes(joystickNum):
    axes = HALJoystickAxes()
    _HALGetJoystickAxes(joystickNum, axes)
    return [x for x in axes.axes[0:axes.count]]

_HALGetJoystickPOVs = _RETFUNC("HALGetJoystickPOVs", C.c_int, ("joystickNum", C.c_uint8), ("povs", HALJoystickPOVs_ptr))
@hal_wrapper
def HALGetJoystickPOVs(joystickNum):
    povs = HALJoystickPOVs()
    _HALGetJoystickPOVs(joystickNum, povs)
    return [x for x in povs.povs[0:povs.count]]

_HALGetJoystickButtons = _RETFUNC("HALGetJoystickButtons", C.c_int, ("joystickNum", C.c_uint8), ("buttons", HALJoystickButtons_ptr))
@hal_wrapper
def HALGetJoystickButtons(joystickNum):
    buttons = HALJoystickButtons()
    _HALGetJoystickButtons(joystickNum, buttons)
    return buttons

_HALGetJoystickDescriptor = _RETFUNC("HALGetJoystickDescriptor", C.c_int, ("joystickNum", C.c_uint8), ("descriptor", HALJoystickDescriptor_ptr))
@hal_wrapper
def HALGetJoystickDescriptor(joystickNum):
    descriptor = HALJoystickDescriptor()
    _HALGetJoystickDescriptor(joystickNum, descriptor)
    return descriptor


HALSetJoystickOutputs = _RETFUNC("HALSetJoystickOutputs", C.c_int, ("joystickNum", C.c_uint8), ("outputs", C.c_uint32), ("leftRumble", C.c_uint16), ("rightRumble", C.c_uint16))

HALGetMatchTime = _RETFUNC("HALGetMatchTime", C.c_int, ("matchTime", C.POINTER(C.c_float)), out=["matchTime"])

HALSetNewDataSem = _RETFUNC("HALSetNewDataSem", None, ("sem", MULTIWAIT_ID))

HALGetSystemActive = _STATUSFUNC("HALGetSystemActive", C.c_bool)
HALGetBrownedOut = _STATUSFUNC("HALGetBrownedOut", C.c_bool)

_HALInitialize = _RETFUNC("HALInitialize", C.c_int, ("mode", C.c_int, 0))
@hal_wrapper
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
@hal_wrapper
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
initializeAnalogOutputPort = _STATUSFUNC("initializeAnalogOutputPort", AnalogPort_ptr, ("port", Port_ptr))
setAnalogOutput = _STATUSFUNC("setAnalogOutput", None, ("analog_port", AnalogPort_ptr), ("voltage", C.c_double))
getAnalogOutput = _STATUSFUNC("getAnalogOutput", C.c_double, ("analog_port", AnalogPort_ptr))
checkAnalogOutputChannel = _RETFUNC("checkAnalogOutputChannel", C.c_bool, ("pin", C.c_uint32))

# Analog input functions
initializeAnalogInputPort = _STATUSFUNC("initializeAnalogInputPort", AnalogPort_ptr, ("port", Port_ptr))
checkAnalogModule = _RETFUNC("checkAnalogModule", C.c_bool, ("module", C.c_uint8))
checkAnalogInputChannel = _RETFUNC("checkAnalogInputChannel", C.c_bool, ("pin", C.c_uint32))

setAnalogSampleRate = _STATUSFUNC("setAnalogSampleRate", None, ("samples_per_second", C.c_double))
getAnalogSampleRate = _STATUSFUNC("getAnalogSampleRate", C.c_float)
setAnalogAverageBits = _STATUSFUNC("setAnalogAverageBits", None, ("analog_port", AnalogPort_ptr), ("bits", C.c_uint32))
getAnalogAverageBits = _STATUSFUNC("getAnalogAverageBits", C.c_uint32, ("analog_port", AnalogPort_ptr))
setAnalogOversampleBits = _STATUSFUNC("setAnalogOversampleBits", None, ("analog_port", AnalogPort_ptr), ("bits", C.c_uint32))
getAnalogOversampleBits = _STATUSFUNC("getAnalogOversampleBits", C.c_uint32, ("analog_port", AnalogPort_ptr))
getAnalogValue = _STATUSFUNC("getAnalogValue", C.c_int16, ("analog_port", AnalogPort_ptr))
getAnalogAverageValue = _STATUSFUNC("getAnalogAverageValue", C.c_int32, ("analog_port", AnalogPort_ptr))
getAnalogVoltsToValue = _STATUSFUNC("getAnalogVoltsToValue", C.c_int32, ("analog_port", AnalogPort_ptr), ("voltage", C.c_double))
getAnalogVoltage = _STATUSFUNC("getAnalogVoltage", C.c_float, ("analog_port", AnalogPort_ptr))
getAnalogAverageVoltage = _STATUSFUNC("getAnalogAverageVoltage", C.c_float, ("analog_port", AnalogPort_ptr))
getAnalogLSBWeight = _STATUSFUNC("getAnalogLSBWeight", C.c_uint32, ("analog_port", AnalogPort_ptr))
getAnalogOffset = _STATUSFUNC("getAnalogOffset", C.c_int32, ("analog_port", AnalogPort_ptr))

isAccumulatorChannel = _STATUSFUNC("isAccumulatorChannel", C.c_bool, ("analog_port", AnalogPort_ptr))
initAccumulator = _STATUSFUNC("initAccumulator", None, ("analog_port", AnalogPort_ptr))
resetAccumulator = _STATUSFUNC("resetAccumulator", None, ("analog_port", AnalogPort_ptr))
setAccumulatorCenter = _STATUSFUNC("setAccumulatorCenter", None, ("analog_port", AnalogPort_ptr), ('center', C.c_int32))
setAccumulatorDeadband = _STATUSFUNC("setAccumulatorDeadband", None, ("analog_port", AnalogPort_ptr), ("deadband", C.c_int32))
getAccumulatorValue = _STATUSFUNC("getAccumulatorValue", C.c_int64, ("analog_port", AnalogPort_ptr))
getAccumulatorCount = _STATUSFUNC("getAccumulatorCount", C.c_uint32, ("analog_port", AnalogPort_ptr))
getAccumulatorOutput = _STATUSFUNC("getAccumulatorOutput", None, ("analog_port", AnalogPort_ptr), ("value", C.POINTER(C.c_int64)), ("count", C.POINTER(C.c_uint32)), out=["value", "count"])

initializeAnalogTrigger = _STATUSFUNC("initializeAnalogTrigger", AnalogTrigger_ptr, ("port", Port_ptr), ("index", C.POINTER(C.c_uint32)), out=["index"])
cleanAnalogTrigger = _STATUSFUNC("cleanAnalogTrigger", None, ("analog_trigger", AnalogTrigger_ptr))
setAnalogTriggerLimitsRaw = _STATUSFUNC("setAnalogTriggerLimitsRaw", None, ("analog_trigger", AnalogTrigger_ptr), ("lower", C.c_int32), ("upper", C.c_int32))
setAnalogTriggerLimitsVoltage = _STATUSFUNC("setAnalogTriggerLimitsVoltage", None, ("analog_trigger", AnalogTrigger_ptr), ("lower", C.c_double), ("upper", C.c_double))
setAnalogTriggerAveraged = _STATUSFUNC("setAnalogTriggerAveraged", None, ("analog_trigger", AnalogTrigger_ptr), ("use_averaged_value", C.c_bool))
setAnalogTriggerFiltered = _STATUSFUNC("setAnalogTriggerFiltered", None, ("analog_trigger", AnalogTrigger_ptr), ("use_filtered_value", C.c_bool))
getAnalogTriggerInWindow = _STATUSFUNC("getAnalogTriggerInWindow", C.c_bool, ("analog_trigger", AnalogTrigger_ptr))
getAnalogTriggerTriggerState = _STATUSFUNC("getAnalogTriggerTriggerState", C.c_bool, ("analog_trigger", AnalogTrigger_ptr))
getAnalogTriggerOutput = _STATUSFUNC("getAnalogTriggerOutput", C.c_bool, ("analog_trigger", AnalogTrigger_ptr), ("type", C.c_int))

#############################################################################
# Compressor
#############################################################################

initializeCompressor = _RETFUNC("initializeCompressor", PCM_ptr, ("module", C.c_uint8))
checkCompressorModule = _RETFUNC("checkCompressorModule", C.c_bool, ("module", C.c_uint8))

getCompressor = _STATUSFUNC("getCompressor", C.c_bool, ("pcm", PCM_ptr))

setClosedLoopControl = _STATUSFUNC("setClosedLoopControl", None, ("pcm", PCM_ptr), ("value", C.c_bool))
getClosedLoopControl = _STATUSFUNC("getClosedLoopControl", C.c_bool, ("pcm", PCM_ptr))

getPressureSwitch = _STATUSFUNC("getPressureSwitch", C.c_bool, ("pcm", PCM_ptr))
getCompressorCurrent = _STATUSFUNC("getCompressorCurrent", C.c_float, ("pcm", PCM_ptr))
getCompressorCurrentTooHighFault = _STATUSFUNC("getCompressorCurrentTooHighFault", C.c_bool, ("pcm", PCM_ptr))
getCompressorCurrentTooHighStickyFault = _STATUSFUNC("getCompressorCurrentTooHighStickyFault", C.c_bool, ("pcm", PCM_ptr))
getCompressorShortedStickyFault = _STATUSFUNC("getCompressorShortedStickyFault", C.c_bool, ("pcm", PCM_ptr))
getCompressorShortedFault = _STATUSFUNC("getCompressorShortedFault", C.c_bool, ("pcm", PCM_ptr))
getCompressorNotConnectedStickyFault = _STATUSFUNC("getCompressorNotConnectedStickyFault", C.c_bool, ("pcm", PCM_ptr))
getCompressorNotConnectedFault = _STATUSFUNC("getCompressorNotConnectedFault", C.c_bool, ("pcm", PCM_ptr))
clearAllPCMStickyFaults = _STATUSFUNC("clearAllPCMStickyFaults", None, ("pcm", PCM_ptr))


#############################################################################
# Digital
#############################################################################

initializeDigitalPort = _STATUSFUNC("initializeDigitalPort", DigitalPort_ptr, ("port", Port_ptr))
checkPWMChannel = _RETFUNC("checkPWMChannel", C.c_bool, ("digital_port", DigitalPort_ptr))
checkRelayChannel = _RETFUNC("checkRelayChannel", C.c_bool, ("digital_port", DigitalPort_ptr))

setPWM = _STATUSFUNC("setPWM", None, ("digital_port", DigitalPort_ptr), ("value", C.c_ushort))
allocatePWMChannel = _STATUSFUNC("allocatePWMChannel", C.c_bool, ("digital_port", DigitalPort_ptr))
freePWMChannel = _STATUSFUNC("freePWMChannel", None, ("digital_port", DigitalPort_ptr))
getPWM = _STATUSFUNC("getPWM", C.c_ushort, ("digital_port", DigitalPort_ptr))
latchPWMZero = _STATUSFUNC("latchPWMZero", None, ("digital_port", DigitalPort_ptr))
setPWMPeriodScale = _STATUSFUNC("setPWMPeriodScale", None, ("digital_port", DigitalPort_ptr), ("squelch_mask", C.c_uint32))

allocatePWM = _STATUSFUNC("allocatePWM", PWM_ptr)
freePWM = _STATUSFUNC("freePWM", None, ("pwm", PWM_ptr))
setPWMRate = _STATUSFUNC("setPWMRate", None, ("rate", C.c_double))
setPWMDutyCycle = _STATUSFUNC("setPWMDutyCycle", None, ("pwm", PWM_ptr), ("duty_cycle", C.c_double))
setPWMOutputChannel = _STATUSFUNC("setPWMOutputChannel", None, ("pwm", PWM_ptr), ("pin", C.c_uint32))

setRelayForward = _STATUSFUNC("setRelayForward", None, ("digital_port", DigitalPort_ptr), ("on", C.c_bool))
setRelayReverse = _STATUSFUNC("setRelayReverse", None, ("digital_port", DigitalPort_ptr), ("on", C.c_bool))
getRelayForward = _STATUSFUNC("getRelayForward", C.c_bool, ("digital_port", DigitalPort_ptr))
getRelayReverse = _STATUSFUNC("getRelayReverse", C.c_bool, ("digital_port", DigitalPort_ptr))

allocateDIO = _STATUSFUNC("allocateDIO", C.c_bool, ("digital_port", DigitalPort_ptr), ("input", C.c_bool))
freeDIO = _STATUSFUNC("freeDIO", None, ("digital_port", DigitalPort_ptr))
setDIO = _STATUSFUNC("setDIO", None, ("digital_port", DigitalPort_ptr), ("value", C.c_short))
getDIO = _STATUSFUNC("getDIO", C.c_bool, ("digital_port", DigitalPort_ptr))
getDIODirection = _STATUSFUNC("getDIODirection", C.c_bool, ("digital_port", DigitalPort_ptr))
pulse = _STATUSFUNC("pulse", None, ("digital_port", DigitalPort_ptr), ("pulse_length", C.c_double))
isPulsing = _STATUSFUNC("isPulsing", C.c_bool, ("digital_port", DigitalPort_ptr))
isAnyPulsing = _STATUSFUNC("isAnyPulsing", C.c_bool)

initializeCounter = _STATUSFUNC("initializeCounter", Counter_ptr, ("mode", C.c_int), ("index", C.POINTER(C.c_uint32)), out=["index"])
freeCounter = _STATUSFUNC("freeCounter", None, ("counter", Counter_ptr))
setCounterAverageSize = _STATUSFUNC("setCounterAverageSize", None, ("counter", Counter_ptr), ("size", C.c_int32))
setCounterUpSource = _STATUSFUNC("setCounterUpSource", None, ("counter", Counter_ptr), ("pin", C.c_uint32), ("analog_trigger", C.c_bool))
setCounterUpSourceEdge = _STATUSFUNC("setCounterUpSourceEdge", None, ("counter", Counter_ptr), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterUpSource = _STATUSFUNC("clearCounterUpSource", None, ("counter", Counter_ptr))
setCounterDownSource = _STATUSFUNC("setCounterDownSource", None, ("counter", Counter_ptr), ("pin", C.c_uint32), ("analog_trigger", C.c_bool))
setCounterDownSourceEdge = _STATUSFUNC("setCounterDownSourceEdge", None, ("counter", Counter_ptr), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterDownSource = _STATUSFUNC("clearCounterDownSource", None, ("counter", Counter_ptr))
setCounterUpDownMode = _STATUSFUNC("setCounterUpDownMode", None, ("counter", Counter_ptr))
setCounterExternalDirectionMode = _STATUSFUNC("setCounterExternalDirectionMode", None, ("counter", Counter_ptr))
setCounterSemiPeriodMode = _STATUSFUNC("setCounterSemiPeriodMode", None, ("counter", Counter_ptr), ("high_semi_period", C.c_bool))
setCounterPulseLengthMode = _STATUSFUNC("setCounterPulseLengthMode", None, ("counter", Counter_ptr), ("threshold", C.c_double))
getCounterSamplesToAverage = _STATUSFUNC("getCounterSamplesToAverage", C.c_int32, ("counter", Counter_ptr))
setCounterSamplesToAverage = _STATUSFUNC("setCounterSamplesToAverage", None, ("counter", Counter_ptr), ("samples_to_average", C.c_int))
resetCounter = _STATUSFUNC("resetCounter", None, ("counter", Counter_ptr))
getCounter = _STATUSFUNC("getCounter", C.c_int32, ("counter", Counter_ptr))
getCounterPeriod = _STATUSFUNC("getCounterPeriod", C.c_double, ("counter", Counter_ptr))
setCounterMaxPeriod = _STATUSFUNC("setCounterMaxPeriod", None, ("counter", Counter_ptr), ("max_period", C.c_double))
setCounterUpdateWhenEmpty = _STATUSFUNC("setCounterUpdateWhenEmpty", None, ("counter", Counter_ptr), ("enabled", C.c_bool))
getCounterStopped = _STATUSFUNC("getCounterStopped", C.c_bool, ("counter", Counter_ptr))
getCounterDirection = _STATUSFUNC("getCounterDirection", C.c_bool, ("counter", Counter_ptr))
setCounterReverseDirection = _STATUSFUNC("setCounterReverseDirection", None, ("counter", Counter_ptr), ("reverse_direction", C.c_bool))

initializeEncoder = _STATUSFUNC("initializeEncoder", Encoder_ptr,
        ("port_a_module", C.c_uint8), ("port_a_pin", C.c_uint32), ("port_a_analog_trigger", C.c_bool),
        ("port_b_module", C.c_uint8), ("port_b_pin", C.c_uint32), ("port_b_analog_trigger", C.c_bool),
        ("reverse_direction", C.c_bool), ("index", C.POINTER(C.c_int32)), out=["index"])
freeEncoder = _STATUSFUNC("freeEncoder", None, ("encoder", Encoder_ptr))
resetEncoder = _STATUSFUNC("resetEncoder", None, ("encoder", Encoder_ptr))
getEncoder = _STATUSFUNC("getEncoder", C.c_int32, ("encoder", Encoder_ptr))
getEncoderPeriod = _STATUSFUNC("getEncoderPeriod", C.c_double, ("encoder", Encoder_ptr))
setEncoderMaxPeriod = _STATUSFUNC("setEncoderMaxPeriod", None, ("encoder", Encoder_ptr), ("max_period", C.c_double))
getEncoderStopped = _STATUSFUNC("getEncoderStopped", C.c_bool, ("encoder", Encoder_ptr))
getEncoderDirection = _STATUSFUNC("getEncoderDirection", C.c_bool, ("encoder", Encoder_ptr))
setEncoderReverseDirection = _STATUSFUNC("setEncoderReverseDirection", None, ("encoder", Encoder_ptr), ("reverse_direction", C.c_bool))
setEncoderSamplesToAverage = _STATUSFUNC("setEncoderSamplesToAverage", None, ("encoder", Encoder_ptr), ("samples_to_average", C.c_uint32))
getEncoderSamplesToAverage = _STATUSFUNC("getEncoderSamplesToAverage", C.c_uint32, ("encoder", Encoder_ptr))
setEncoderIndexSource = _STATUSFUNC("setEncoderIndexSource", None, ("encoder", Encoder_ptr), ("pin", C.c_uint32), ("analogTrigger", C.c_bool), ("activeHigh", C.c_bool), ("edgeSensitive", C.c_bool))

getLoopTiming = _STATUSFUNC("getLoopTiming", C.c_uint16)

spiInitialize = _STATUSFUNC("spiInitialize", None, ("port", C.c_uint8))

_spiTransaction = _RETFUNC("spiTransaction", C.c_int32, ("port", C.c_uint8),
                           ("data_to_send", C.POINTER(C.c_uint8)), ("data_received", C.POINTER(C.c_uint8)), ("size", C.c_uint8))
@hal_wrapper
def spiTransaction(port, data_to_send):
    size = len(data_to_send)
    send_buffer = (C.c_uint8 * size)(*data_to_send)
    recv_buffer = C.c_uint8 * size
    rv = _spiTransaction(port, send_buffer, recv_buffer, size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return [x for x in recv_buffer]

_spiWrite = _RETFUNC("spiWrite", C.c_int32, ("port", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
@hal_wrapper
def spiWrite(port, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _spiWrite(port, buffer, send_size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))

_spiRead = _RETFUNC("spiRead", C.c_int32, ("port", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
@hal_wrapper
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
@hal_wrapper
def i2CTransaction(port, device_address, data_to_send, receive_size):
    send_size = len(data_to_send)
    send_buffer = (C.c_uint8 * send_size)(*data_to_send)
    recv_buffer = C.c_uint8 * receive_size
    rv = _i2CTransaction(port, device_address, send_buffer, send_size, recv_buffer, receive_size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return [x for x in recv_buffer]

_i2CWrite = _RETFUNC("i2CWrite", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("data_to_send", C.POINTER(C.c_uint8)), ("send_size", C.c_uint8))
@hal_wrapper
def i2CWrite(port, device_address, data_to_send):
    send_size = len(data_to_send)
    buffer = (C.c_uint8 * send_size)(*data_to_send)
    rv = _i2CWrite(port, device_address, buffer, send_size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))

_i2CRead = _RETFUNC("i2CRead", C.c_int32, ("port", C.c_uint8), ("device_address", C.c_uint8), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_uint8))
@hal_wrapper
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

initializeInterrupts = _STATUSFUNC("initializeInterrupts", Interrupt_ptr, ("interrupt_index", C.c_uint32), ("watcher", C.c_bool))
_cleanInterrupts = _STATUSFUNC("cleanInterrupts", None, ("interrupt", Interrupt_ptr))
@hal_wrapper
def cleanInterrupts(interrupt):
    _cleanInterrupts(interrupt)

    # remove references to function handlers
    _interruptHandlers.pop(interrupt, None)

waitForInterrupt = _STATUSFUNC("waitForInterrupt", C.c_uint32, ("interrupt", Interrupt_ptr), ("timeout", C.c_double), ("ignorePrevious", C.c_bool))
enableInterrupts = _STATUSFUNC("enableInterrupts", None, ("interrupt", Interrupt_ptr))
disableInterrupts = _STATUSFUNC("disableInterrupts", None, ("interrupt", Interrupt_ptr))
readRisingTimestamp = _STATUSFUNC("readRisingTimestamp", C.c_double, ("interrupt", Interrupt_ptr))
readFallingTimestamp = _STATUSFUNC("readFallingTimestamp", C.c_double, ("interrupt", Interrupt_ptr))
requestInterrupts = _STATUSFUNC("requestInterrupts", None, ("interrupt", Interrupt_ptr), ("routing_module", C.c_uint8), ("routing_pin", C.c_uint32), ("routing_analog_trigger", C.c_bool))

_attachInterruptHandler = _STATUSFUNC("attachInterruptHandler", None, ("interrupt", Interrupt_ptr), ("handler", _InterruptHandlerFunction), ("param", C.c_void_p))
@hal_wrapper
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

setInterruptUpSourceEdge = _STATUSFUNC("setInterruptUpSourceEdge", None, ("interrupt", Interrupt_ptr), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))

#############################################################################
# Notifier
#############################################################################

_NotifierProcessQueueFunction = C.CFUNCTYPE(None, C.c_uint32, C.c_void_p)
_notifierProcessQueueFunctions = {}

_initializeNotifier = _STATUSFUNC("initializeNotifier", Notifier_ptr, ("processQueue", _NotifierProcessQueueFunction))
@hal_wrapper
def initializeNotifier(processQueue):
    # While initializeNotifier provides a param parameter, we use ctypes
    # magic instead to uniquify the callback handler

    # create bounce function to drop param
    cb_func = _NotifierProcessQueueFunction(lambda mask, param: processQueue(mask))

    # initialize notifier
    notifier = _attachInterruptHandler(processQueue, cb_func, None)

    # keep reference to bounce function
    handlers = _notifierProcessQueueFunctions[notifier] = cb_func

_cleanNotifier = _STATUSFUNC("cleanNotifier", None, ("notifier", Notifier_ptr))
@hal_wrapper
def cleanNotifier(notifier):
    _cleanNotifier(notifier)

    # remove reference to process queue function
    _notifierProcessQueueFunctions.pop(notifier, None)

updateNotifierAlarm = _STATUSFUNC("updateNotifierAlarm", None, ("notifier", Notifier_ptr), ("triggerTime", C.c_uint32))

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

initializeSolenoidPort = _STATUSFUNC("initializeSolenoidPort", SolenoidPort_ptr, ("port", Port_ptr))
checkSolenoidModule = _RETFUNC("checkSolenoidModule", C.c_bool, ("module", C.c_uint8))

getSolenoid = _STATUSFUNC("getSolenoid", C.c_bool, ("solenoid_port", SolenoidPort_ptr))
setSolenoid = _STATUSFUNC("setSolenoid", None, ("solenoid_port", SolenoidPort_ptr), ("value", C.c_bool))

getPCMSolenoidBlackList = _STATUSFUNC("getPCMSolenoidBlackList", C.c_int, ("solenoid_port", SolenoidPort_ptr))
getPCMSolenoidVoltageStickyFault = _STATUSFUNC("getPCMSolenoidVoltageStickyFault", C.c_bool, ("solenoid_port", SolenoidPort_ptr))
getPCMSolenoidVoltageFault = _STATUSFUNC("getPCMSolenoidVoltageFault", C.c_bool, ("solenoid_port", SolenoidPort_ptr))
clearAllPCMStickyFaults_sol = _STATUSFUNC("clearAllPCMStickyFaults_sol", None, ("solenoid_port", SolenoidPort_ptr))

#############################################################################
# TalonSRX
#############################################################################
TalonSRX_Create = _RETFUNC("c_TalonSRX_Create", TalonSRX_ptr, ("deviceNumber", C.c_int), ("controlPeriodMs", C.c_int))
TalonSRX_Destroy = _RETFUNC("c_TalonSRX_Destroy", None, ("handle", TalonSRX_ptr))
TalonSRX_SetParam = _CTRFUNC("c_TalonSRX_SetParam", ("handle", TalonSRX_ptr), ("paramEnum", C.c_int), ("value", C.c_double))
TalonSRX_RequestParam = _CTRFUNC("c_TalonSRX_RequestParam", ("handle", TalonSRX_ptr), ("paramEnum", C.c_int))
TalonSRX_GetParamResponse = _CTRFUNC("c_TalonSRX_GetParamResponse", ("handle", TalonSRX_ptr), ("paramEnum", C.c_int), ("value", C.POINTER(C.c_double)), out=["value"])
TalonSRX_GetParamResponseInt32 = _CTRFUNC("c_TalonSRX_GetParamResponseInt32", ("handle", TalonSRX_ptr), ("paramEnum", C.c_int), ("value", C.POINTER(C.c_int)), out=["value"])
TalonSRX_SetStatusFrameRate = _CTRFUNC("c_TalonSRX_SetStatusFrameRate", ("handle", TalonSRX_ptr), ("frameEnum", C.c_uint), ("periodMs", C.c_uint))
TalonSRX_ClearStickyFaults = _CTRFUNC("c_TalonSRX_ClearStickyFaults", ("handle", TalonSRX_ptr))
TalonSRX_GetFault_OverTemp = _CTRFUNC("c_TalonSRX_GetFault_OverTemp", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_UnderVoltage = _CTRFUNC("c_TalonSRX_GetFault_UnderVoltage", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_ForLim = _CTRFUNC("c_TalonSRX_GetFault_ForLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_RevLim = _CTRFUNC("c_TalonSRX_GetFault_RevLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_HardwareFailure = _CTRFUNC("c_TalonSRX_GetFault_HardwareFailure", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_ForSoftLim = _CTRFUNC("c_TalonSRX_GetFault_ForSoftLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFault_RevSoftLim = _CTRFUNC("c_TalonSRX_GetFault_RevSoftLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_OverTemp = _CTRFUNC("c_TalonSRX_GetStckyFault_OverTemp", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_UnderVoltage = _CTRFUNC("c_TalonSRX_GetStckyFault_UnderVoltage", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_ForLim = _CTRFUNC("c_TalonSRX_GetStckyFault_ForLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_RevLim = _CTRFUNC("c_TalonSRX_GetStckyFault_RevLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_ForSoftLim = _CTRFUNC("c_TalonSRX_GetStckyFault_ForSoftLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetStckyFault_RevSoftLim = _CTRFUNC("c_TalonSRX_GetStckyFault_RevSoftLim", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetAppliedThrottle = _CTRFUNC("c_TalonSRX_GetAppliedThrottle", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetCloseLoopErr = _CTRFUNC("c_TalonSRX_GetCloseLoopErr", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFeedbackDeviceSelect = _CTRFUNC("c_TalonSRX_GetFeedbackDeviceSelect", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetModeSelect = _CTRFUNC("c_TalonSRX_GetModeSelect", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetLimitSwitchEn = _CTRFUNC("c_TalonSRX_GetLimitSwitchEn", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetLimitSwitchClosedFor = _CTRFUNC("c_TalonSRX_GetLimitSwitchClosedFor", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetLimitSwitchClosedRev = _CTRFUNC("c_TalonSRX_GetLimitSwitchClosedRev", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetSensorPosition = _CTRFUNC("c_TalonSRX_GetSensorPosition", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetSensorVelocity = _CTRFUNC("c_TalonSRX_GetSensorVelocity", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetCurrent = _CTRFUNC("c_TalonSRX_GetCurrent", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_double)), out=["param"])
TalonSRX_GetBrakeIsEnabled = _CTRFUNC("c_TalonSRX_GetBrakeIsEnabled", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetEncPosition = _CTRFUNC("c_TalonSRX_GetEncPosition", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetEncVel = _CTRFUNC("c_TalonSRX_GetEncVel", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetEncIndexRiseEvents = _CTRFUNC("c_TalonSRX_GetEncIndexRiseEvents", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetQuadApin = _CTRFUNC("c_TalonSRX_GetQuadApin", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetQuadBpin = _CTRFUNC("c_TalonSRX_GetQuadBpin", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetQuadIdxpin = _CTRFUNC("c_TalonSRX_GetQuadIdxpin", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetAnalogInWithOv = _CTRFUNC("c_TalonSRX_GetAnalogInWithOv", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetAnalogInVel = _CTRFUNC("c_TalonSRX_GetAnalogInVel", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetTemp = _CTRFUNC("c_TalonSRX_GetTemp", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_double)), out=["param"])
TalonSRX_GetBatteryV = _CTRFUNC("c_TalonSRX_GetBatteryV", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_double)), out=["param"])
TalonSRX_GetResetCount = _CTRFUNC("c_TalonSRX_GetResetCount", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetResetFlags = _CTRFUNC("c_TalonSRX_GetResetFlags", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_GetFirmVers = _CTRFUNC("c_TalonSRX_GetFirmVers", ("handle", TalonSRX_ptr), ("param", C.POINTER(C.c_int)), out=["param"])
TalonSRX_SetDemand = _CTRFUNC("c_TalonSRX_SetDemand", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetOverrideLimitSwitchEn = _CTRFUNC("c_TalonSRX_SetOverrideLimitSwitchEn", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetFeedbackDeviceSelect = _CTRFUNC("c_TalonSRX_SetFeedbackDeviceSelect", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetRevMotDuringCloseLoopEn = _CTRFUNC("c_TalonSRX_SetRevMotDuringCloseLoopEn", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetOverrideBrakeType = _CTRFUNC("c_TalonSRX_SetOverrideBrakeType", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetModeSelect = _CTRFUNC("c_TalonSRX_SetModeSelect", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetModeSelect2 = _CTRFUNC("c_TalonSRX_SetModeSelect2", ("handle", TalonSRX_ptr), ("modeSelect", C.c_int), ("demand", C.c_int))
TalonSRX_SetProfileSlotSelect = _CTRFUNC("c_TalonSRX_SetProfileSlotSelect", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetRampThrottle = _CTRFUNC("c_TalonSRX_SetRampThrottle", ("handle", TalonSRX_ptr), ("param", C.c_int))
TalonSRX_SetRevFeedbackSensor = _CTRFUNC("c_TalonSRX_SetRevFeedbackSensor", ("handle", TalonSRX_ptr), ("param", C.c_int))

#############################################################################
# Utilities
#############################################################################
HAL_NO_WAIT = _VAR("HAL_NO_WAIT", C.c_int32)
HAL_WAIT_FOREVER = _VAR("HAL_WAIT_FOREVER", C.c_int32)

delayTicks = _RETFUNC("delayTicks", None, ("ticks", C.c_int32))
delayMillis = _RETFUNC("delayMillis", None, ("ms", C.c_double))
delaySeconds = _RETFUNC("delaySeconds", None, ("s", C.c_double))
