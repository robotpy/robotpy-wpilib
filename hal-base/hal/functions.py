import ctypes as C
import os as _os
import warnings

from .exceptions import HALError
from .constants import *

from hal_impl.types import *
from hal_impl.fndef import _RETFUNC, _THUNKFUNC, _VAR, _dll, sleep
from hal_impl import __hal_simulation__

def hal_wrapper(f):
    '''Decorator to support introspection. The wrapped function must be
       the same name as the wrapper function, but start with an underscore
    '''
    
    wrapped = globals()['_' + f.__name__]
    if hasattr(wrapped, 'fndata'):
        f.fndata = wrapped.fndata
    return f

def _STATUSFUNC(name, restype, *params, out=None, library=_dll,
                handle_missing=False, _inner_func=_RETFUNC, c_name=None):
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
    _inner = _inner_func(name, restype, *realparams, out=out, library=library,
                        errcheck=errcheck, handle_missing=handle_missing, c_name=None)
    def outer(*args, **kwargs):
        status = C.c_int32(0)
        rv = _inner(*args, status=status, **kwargs)
        if status.value == 0:
            return rv
        elif status.value < 0:
            raise HALError(getErrorMessage(status.value))
        elif status.value > 0:
            warnings.warn(getErrorMessage(status.value), stacklevel=2)
            return rv
    
    # Support introspection for API validation
    if hasattr(_inner, 'fndata'):
        outer.fndata = _inner.fndata
    return outer

def _TSTATUSFUNC(*a, **k):
    return _STATUSFUNC(_inner_func=_THUNKFUNC, *a, **k)


#############################################################################
# Python-specific hal functions
#############################################################################

def isSimulation():
    return __hal_simulation__

HALIsSimulation = isSimulation

#############################################################################
# HAL
#############################################################################

getPort = _RETFUNC("getPort", PortHandle, ("pin", C.c_int32))
getPortWithModule = _RETFUNC("getPortWithModule", PortHandle, ("module", C.c_int32), ("pin", C.c_int32))

_getErrorMessage = _RETFUNC("getErrorMessage", C.c_char_p, ("code", C.c_int32))
@hal_wrapper
def getErrorMessage(code):
    return _getErrorMessage(code).decode('utf_8')

getFPGAVersion = _STATUSFUNC("getFPGAVersion", C.c_int32)
getFPGARevision = _STATUSFUNC("getFPGARevision", C.c_uint64)
getFPGATime = _STATUSFUNC("getFPGATime", C.c_uint64)

getRuntimeType = _RETFUNC("getRuntimeType", C.c_int32)
getFPGAButton = _STATUSFUNC("getFPGAButton", C.c_bool)

getSystemActive = _STATUSFUNC("getSystemActive", C.c_bool)
getBrownedOut = _STATUSFUNC("getBrownedOut", C.c_bool)

_initialize = _RETFUNC("initialize", C.c_int32, ("mode", C.c_int32))

@hal_wrapper
def initialize(mode = 0):
    rv = _initialize(mode)
    if not rv:
        raise HALError("Could not initialize HAL")

_report = _RETFUNC("report", C.c_int64,
                   ("resource", C.c_int32), ("instanceNumber", C.c_int32),
                   ("context", C.c_int32, 0), ("feature", C.c_char_p, None))
@hal_wrapper
def report(resource, instanceNumber, context = 0, feature = None):
    if feature is not None:
        feature = feature.encode('utf-8')
    return _report(resource, instanceNumber, context, feature)


#############################################################################
# Accelerometer.h
#############################################################################

setAccelerometerActive = _RETFUNC("setAccelerometerActive", None, ("active", C.c_bool))
setAccelerometerRange = _RETFUNC("setAccelerometerRange", None, ("range", C.c_int))
getAccelerometerX = _RETFUNC("getAccelerometerX", C.c_double)
getAccelerometerY = _RETFUNC("getAccelerometerY", C.c_double)
getAccelerometerZ = _RETFUNC("getAccelerometerZ", C.c_double)


#############################################################################
# AnalogAccumulator.h
#############################################################################

isAccumulatorChannel = _STATUSFUNC("isAccumulatorChannel", C.c_bool, ("analog_port", AnalogInputHandle))
initAccumulator = _STATUSFUNC("initAccumulator", None, ("analog_port", AnalogInputHandle))
resetAccumulator = _STATUSFUNC("resetAccumulator", None, ("analog_port", AnalogInputHandle))
setAccumulatorCenter = _STATUSFUNC("setAccumulatorCenter", None, ("analog_port", AnalogInputHandle), ('center', C.c_int32))
setAccumulatorDeadband = _STATUSFUNC("setAccumulatorDeadband", None, ("analog_port", AnalogInputHandle), ("deadband", C.c_int32))
getAccumulatorValue = _STATUSFUNC("getAccumulatorValue", C.c_int64, ("analog_port", AnalogInputHandle))
getAccumulatorCount = _STATUSFUNC("getAccumulatorCount", C.c_int64, ("analog_port", AnalogInputHandle))
getAccumulatorOutput = _STATUSFUNC("getAccumulatorOutput", None, ("analog_port", AnalogInputHandle), ("value", C.POINTER(C.c_int64)), ("count", C.POINTER(C.c_int64)), out=["value", "count"])


#############################################################################
# AnalogGyro.h
#############################################################################

initializeAnalogGyro = _STATUSFUNC("initializeAnalogGyro", GyroHandle, ("handle", AnalogInputHandle))
setupAnalogGyro = _STATUSFUNC("setupAnalogGyro", None, ("handle", GyroHandle))
freeAnalogGyro = _RETFUNC("freeAnalogGyro", None, ("handle", GyroHandle))
setAnalogGyroParameters = _STATUSFUNC("setAnalogGyroParameters", None, ("handle", GyroHandle), ("voltsPerDegreePerSecond", C.c_double), ("offset", C.c_double), ("center", C.c_int32))
setAnalogGyroVoltsPerDegreePerSecond = _STATUSFUNC("setAnalogGyroVoltsPerDegreePerSecond", None, ("handle", GyroHandle), ("voltsPerDegreePerSecond", C.c_double))
resetAnalogGyro = _STATUSFUNC("resetAnalogGyro", None, ("handle", GyroHandle))
calibrateAnalogGyro = _STATUSFUNC("calibrateAnalogGyro", None, ("handle", GyroHandle))
setAnalogGyroDeadband = _STATUSFUNC("setAnalogGyroDeadband", None, ("handle", GyroHandle), ("volts", C.c_double))
getAnalogGyroAngle = _STATUSFUNC("getAnalogGyroAngle", C.c_double, ("handle", GyroHandle))
getAnalogGyroRate = _STATUSFUNC("getAnalogGyroRate", C.c_double, ("handle", GyroHandle))
getAnalogGyroOffset = _STATUSFUNC("getAnalogGyroOffset", C.c_double, ("handle", GyroHandle))
getAnalogGyroCenter = _STATUSFUNC("getAnalogGyroCenter", C.c_int32, ("handle", GyroHandle))


#############################################################################
# AnalogInput.h
#############################################################################

initializeAnalogInputPort = _STATUSFUNC("initializeAnalogInputPort", AnalogInputHandle, ("port", PortHandle))
freeAnalogInputPort = _RETFUNC("freeAnalogInputPort", None, ("analog_port", AnalogInputHandle))
checkAnalogModule = _RETFUNC("checkAnalogModule", C.c_bool, ("module", C.c_int32))
checkAnalogInputChannel = _RETFUNC("checkAnalogInputChannel", C.c_bool, ("pin", C.c_int32))

setAnalogSampleRate = _STATUSFUNC("setAnalogSampleRate", None, ("samples_per_second", C.c_double))
getAnalogSampleRate = _STATUSFUNC("getAnalogSampleRate", C.c_double)
setAnalogAverageBits = _STATUSFUNC("setAnalogAverageBits", None, ("analog_port", AnalogInputHandle), ("bits", C.c_int32))
getAnalogAverageBits = _STATUSFUNC("getAnalogAverageBits", C.c_int32, ("analog_port", AnalogInputHandle))
setAnalogOversampleBits = _STATUSFUNC("setAnalogOversampleBits", None, ("analog_port", AnalogInputHandle), ("bits", C.c_int32))
getAnalogOversampleBits = _STATUSFUNC("getAnalogOversampleBits", C.c_int32, ("analog_port", AnalogInputHandle))
getAnalogValue = _STATUSFUNC("getAnalogValue", C.c_int32, ("analog_port", AnalogInputHandle))
getAnalogAverageValue = _STATUSFUNC("getAnalogAverageValue", C.c_int32, ("analog_port", AnalogInputHandle))
getAnalogVoltsToValue = _STATUSFUNC("getAnalogVoltsToValue", C.c_int32, ("analog_port", AnalogInputHandle), ("voltage", C.c_double))
getAnalogVoltage = _STATUSFUNC("getAnalogVoltage", C.c_double, ("analog_port", AnalogInputHandle))
getAnalogAverageVoltage = _STATUSFUNC("getAnalogAverageVoltage", C.c_double, ("analog_port", AnalogInputHandle))
getAnalogLSBWeight = _STATUSFUNC("getAnalogLSBWeight", C.c_int32, ("analog_port", AnalogInputHandle))
getAnalogOffset = _STATUSFUNC("getAnalogOffset", C.c_int32, ("analog_port", AnalogInputHandle))


#############################################################################
# AnalogOutput.h
#############################################################################

initializeAnalogOutputPort = _STATUSFUNC("initializeAnalogOutputPort", AnalogOutputHandle, ("port", PortHandle))
freeAnalogOutputPort = _RETFUNC("freeAnalogOutputPort", None, ("analog_port", AnalogOutputHandle))
setAnalogOutput = _STATUSFUNC("setAnalogOutput", None, ("analog_port", AnalogOutputHandle), ("voltage", C.c_double))
getAnalogOutput = _STATUSFUNC("getAnalogOutput", C.c_double, ("analog_port", AnalogOutputHandle))
checkAnalogOutputChannel = _RETFUNC("checkAnalogOutputChannel", C.c_bool, ("pin", C.c_int32))


#############################################################################
# AnalogTrigger.h
#############################################################################

initializeAnalogTrigger = _STATUSFUNC("initializeAnalogTrigger", AnalogTriggerHandle, ("port", AnalogInputHandle), ("index", C.POINTER(C.c_int32)), out=["index"])
cleanAnalogTrigger = _STATUSFUNC("cleanAnalogTrigger", None, ("analog_trigger", AnalogTriggerHandle))
setAnalogTriggerLimitsRaw = _STATUSFUNC("setAnalogTriggerLimitsRaw", None, ("analog_trigger", AnalogTriggerHandle), ("lower", C.c_int32), ("upper", C.c_int32))
setAnalogTriggerLimitsVoltage = _STATUSFUNC("setAnalogTriggerLimitsVoltage", None, ("analog_trigger", AnalogTriggerHandle), ("lower", C.c_double), ("upper", C.c_double))
setAnalogTriggerAveraged = _STATUSFUNC("setAnalogTriggerAveraged", None, ("analog_trigger", AnalogTriggerHandle), ("use_averaged_value", C.c_bool))
setAnalogTriggerFiltered = _STATUSFUNC("setAnalogTriggerFiltered", None, ("analog_trigger", AnalogTriggerHandle), ("use_filtered_value", C.c_bool))
getAnalogTriggerInWindow = _STATUSFUNC("getAnalogTriggerInWindow", C.c_bool, ("analog_trigger", AnalogTriggerHandle))
getAnalogTriggerTriggerState = _STATUSFUNC("getAnalogTriggerTriggerState", C.c_bool, ("analog_trigger", AnalogTriggerHandle))
getAnalogTriggerOutput = _STATUSFUNC("getAnalogTriggerOutput", C.c_bool, ("analog_trigger", AnalogTriggerHandle), ("type", C.c_int))


#############################################################################
# CAN.h
#############################################################################

# Not implemented 


#############################################################################
# Compressor.h
#############################################################################

initializeCompressor = _STATUSFUNC("initializeCompressor", CompressorHandle, ("module", C.c_int32))
checkCompressorModule = _RETFUNC("checkCompressorModule", C.c_bool, ("module", C.c_int32))

getCompressor = _STATUSFUNC("getCompressor", C.c_bool, ("compressorHandle", CompressorHandle))

setCompressorClosedLoopControl = _STATUSFUNC("setCompressorClosedLoopControl", None, ("compressorHandle", CompressorHandle), ("value", C.c_bool))
getCompressorClosedLoopControl = _STATUSFUNC("getCompressorClosedLoopControl", C.c_bool, ("compressorHandle", CompressorHandle))

getCompressorPressureSwitch = _STATUSFUNC("getCompressorPressureSwitch", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorCurrent = _STATUSFUNC("getCompressorCurrent", C.c_double, ("compressorHandle", CompressorHandle))
getCompressorCurrentTooHighFault = _STATUSFUNC("getCompressorCurrentTooHighFault", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorCurrentTooHighStickyFault = _STATUSFUNC("getCompressorCurrentTooHighStickyFault", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorShortedStickyFault = _STATUSFUNC("getCompressorShortedStickyFault", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorShortedFault = _STATUSFUNC("getCompressorShortedFault", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorNotConnectedStickyFault = _STATUSFUNC("getCompressorNotConnectedStickyFault", C.c_bool, ("compressorHandle", CompressorHandle))
getCompressorNotConnectedFault = _STATUSFUNC("getCompressorNotConnectedFault", C.c_bool, ("compressorHandle", CompressorHandle))


#############################################################################
# Constants.h
#############################################################################

getSystemClockTicksPerMicrosecond = _RETFUNC("getSystemClockTicksPerMicrosecond", C.c_int32)


#############################################################################
# Counter.h
#############################################################################

initializeCounter = _STATUSFUNC("initializeCounter", CounterHandle, ("mode", C.c_int), ("index", C.POINTER(C.c_int32)), out=["index"])
freeCounter = _STATUSFUNC("freeCounter", None, ("counterHandle", CounterHandle))
setCounterAverageSize = _STATUSFUNC("setCounterAverageSize", None, ("counterHandle", CounterHandle), ("size", C.c_int32))
setCounterUpSource = _STATUSFUNC("setCounterUpSource", None, ("counterHandle", CounterHandle), ("digitalSourceHandle", Handle), ("analogTriggerType", C.c_int32))
setCounterUpSourceEdge = _STATUSFUNC("setCounterUpSourceEdge", None, ("counterHandle", CounterHandle), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterUpSource = _STATUSFUNC("clearCounterUpSource", None, ("counterHandle", CounterHandle))
setCounterDownSource = _STATUSFUNC("setCounterDownSource", None, ("counterHandle", CounterHandle), ("digitalSourceHandle", Handle), ("analogTriggerType", C.c_int32))
setCounterDownSourceEdge = _STATUSFUNC("setCounterDownSourceEdge", None, ("counterHandle", CounterHandle), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))
clearCounterDownSource = _STATUSFUNC("clearCounterDownSource", None, ("counterHandle", CounterHandle))
setCounterUpDownMode = _STATUSFUNC("setCounterUpDownMode", None, ("counterHandle", CounterHandle))
setCounterExternalDirectionMode = _STATUSFUNC("setCounterExternalDirectionMode", None, ("counterHandle", CounterHandle))
setCounterSemiPeriodMode = _STATUSFUNC("setCounterSemiPeriodMode", None, ("counterHandle", CounterHandle), ("high_semi_period", C.c_bool))
setCounterPulseLengthMode = _STATUSFUNC("setCounterPulseLengthMode", None, ("counterHandle", CounterHandle), ("threshold", C.c_double))
getCounterSamplesToAverage = _STATUSFUNC("getCounterSamplesToAverage", C.c_int32, ("counterHandle", CounterHandle))
setCounterSamplesToAverage = _STATUSFUNC("setCounterSamplesToAverage", None, ("counterHandle", CounterHandle), ("samples_to_average", C.c_int))
resetCounter = _STATUSFUNC("resetCounter", None, ("counterHandle", CounterHandle))
getCounter = _STATUSFUNC("getCounter", C.c_int32, ("counterHandle", CounterHandle))
getCounterPeriod = _STATUSFUNC("getCounterPeriod", C.c_double, ("counterHandle", CounterHandle))
setCounterMaxPeriod = _STATUSFUNC("setCounterMaxPeriod", None, ("counterHandle", CounterHandle), ("max_period", C.c_double))
setCounterUpdateWhenEmpty = _STATUSFUNC("setCounterUpdateWhenEmpty", None, ("counterHandle", CounterHandle), ("enabled", C.c_bool))
getCounterStopped = _STATUSFUNC("getCounterStopped", C.c_bool, ("counterHandle", CounterHandle))
getCounterDirection = _STATUSFUNC("getCounterDirection", C.c_bool, ("counterHandle", CounterHandle))
setCounterReverseDirection = _STATUSFUNC("setCounterReverseDirection", None, ("counterHandle", CounterHandle), ("reverse_direction", C.c_bool))


#############################################################################
# DIO.h
#############################################################################

initializeDIOPort = _STATUSFUNC("initializeDIOPort", DigitalHandle, ("portHandle", PortHandle), ("input", C.c_bool))
checkDIOChannel = _RETFUNC("checkDIOChannel", C.c_bool, ("channel", C.c_int32))
freeDIOPort = _RETFUNC("freeDIOPort", None, ("dioPortHandle", DigitalHandle))
allocateDigitalPWM = _STATUSFUNC("allocateDigitalPWM", DigitalPWMHandle)
freeDigitalPWM = _STATUSFUNC("freeDigitalPWM", None, ("pwmGenerator", DigitalPWMHandle))
setDigitalPWMRate = _STATUSFUNC("setDigitalPWMRate", None, ("rate", C.c_double))
setDigitalPWMDutyCycle = _STATUSFUNC("setDigitalPWMDutyCycle", None, ("pwmGenerator", DigitalPWMHandle), ("dutyCycle", C.c_double))
setDigitalPWMOutputChannel = _STATUSFUNC("setDigitalPWMOutputChannel", None, ("pwmGenerator", DigitalPWMHandle), ("channel", C.c_int32))

setDIO = _STATUSFUNC("setDIO", None, ("dioPortHandle", DigitalHandle), ("value", C.c_bool))
getDIO = _STATUSFUNC("getDIO", C.c_bool, ("dioPortHandle", DigitalHandle))
getDIODirection = _STATUSFUNC("getDIODirection", C.c_bool, ("dioPortHandle", DigitalHandle))
pulse = _STATUSFUNC("pulse", None, ("dioPortHandle", DigitalHandle), ("pulse_length", C.c_double))
isPulsing = _STATUSFUNC("isPulsing", C.c_bool, ("dioPortHandle", DigitalHandle))
isAnyPulsing = _STATUSFUNC("isAnyPulsing", C.c_bool)

setFilterSelect = _STATUSFUNC("setFilterSelect", None, ("dioPortHandle", DigitalHandle), ("filterIndex", C.c_int32))
getFilterSelect = _STATUSFUNC("getFilterSelect", C.c_int32, ("dioPortHandle", DigitalHandle))
setFilterPeriod = _STATUSFUNC("setFilterPeriod", None, ("filterIndex", C.c_int32), ("value", C.c_int64))
getFilterPeriod = _STATUSFUNC("getFilterPeriod", C.c_int64, ("filterIndex", C.c_int32))


#############################################################################
# DriverStation.h
#############################################################################

setErrorData = _RETFUNC("setErrorData", C.c_int32, ("errors", C.c_char_p), ("errorsLength", C.c_int32), ("waitMs", C.c_int32))
sendError = _RETFUNC("sendError", C.c_int32, ("isError", C.c_bool), ("errorCode", C.c_int32), ("isLVCode", C.c_bool), ("details", C.c_char_p), ("location", C.c_char_p), ("callStack", C.c_char_p), ("printMsg", C.c_bool))
getControlWord = _RETFUNC("getControlWord", C.c_int32, ("controlWord", ControlWord_ptr))
getAllianceStation = _STATUSFUNC("getAllianceStation", C.c_int32)
getJoystickAxes = _RETFUNC("getJoystickAxes", C.c_int32, ("joystickNum", C.c_int32), ("axes", JoystickAxes_ptr))
getJoystickPOVs = _RETFUNC("getJoystickPOVs", C.c_int32, ("joystickNum", C.c_int32), ("povs", JoystickPOVs_ptr))
getJoystickButtons = _RETFUNC("getJoystickButtons", C.c_int32, ("joystickNum", C.c_int32), ("buttons", JoystickButtons_ptr))
getJoystickDescriptor = _RETFUNC("getJoystickDescriptor", C.c_int32, ("joystickNum", C.c_int32), ("desc", JoystickDescriptor_ptr))
getJoystickIsXbox = _RETFUNC("getJoystickIsXbox", C.c_bool, ("joystickNum", C.c_int32))
getJoystickType = _RETFUNC("getJoystickType", C.c_int32, ("joystickNum", C.c_int32))
getJoystickName = _RETFUNC("getJoystickName", C.c_char_p, ("joystickNum", C.c_int32))
getJoystickAxisType = _RETFUNC("getJoystickAxisType", C.c_int32, ("joystickNum", C.c_int32), ("axis", C.c_int32))
setJoystickOutputs = _RETFUNC("setJoystickOutputs", C.c_int32, ("joystickNum", C.c_int32), ("outputs", C.c_int64), ("leftRumble", C.c_int32), ("rightRumble", C.c_int32))

getMatchTime = _STATUSFUNC("getMatchTime", C.c_double)
waitForDSData = _RETFUNC("waitForDSData", None)

initializeDriverStation = _RETFUNC("initializeDriverStation", None)
observeUserProgramStarting = _RETFUNC("observeUserProgramStarting", None)
observeUserProgramDisabled = _RETFUNC("observeUserProgramDisabled", None)
observeUserProgramAutonomous = _RETFUNC("observeUserProgramAutonomous", None)
observeUserProgramTeleop = _RETFUNC("observeUserProgramTeleop", None)
observeUserProgramTest = _RETFUNC("observeUserProgramTest", None)


#############################################################################
# Encoder
#############################################################################

initializeEncoder = _STATUSFUNC("initializeEncoder", EncoderHandle,
            ("digitalSourceHandleA", Handle), ("analogTriggerTypeA", C.c_int32),
            ("digitalSourceHandleB", Handle), ("analogTriggerTypeB", C.c_int32),
            ("reverseDirection", C.c_bool), ("encodingType", C.c_int32))

freeEncoder = _STATUSFUNC("freeEncoder", None, ("encoder", EncoderHandle))

getEncoder = _STATUSFUNC("getEncoder", C.c_int32, ("encoder", EncoderHandle))
getEncoderRaw = _STATUSFUNC("getEncoderRaw", C.c_int32, ("encoderHandle", EncoderHandle))
getEncoderEncodingScale = _STATUSFUNC("getEncoderEncodingScale", C.c_int32, ("encoderHandle", EncoderHandle))
resetEncoder = _STATUSFUNC("resetEncoder", None, ("encoder", EncoderHandle))
getEncoderPeriod = _STATUSFUNC("getEncoderPeriod", C.c_double, ("encoder", EncoderHandle))
setEncoderMaxPeriod = _STATUSFUNC("setEncoderMaxPeriod", None, ("encoder", EncoderHandle), ("max_period", C.c_double))
getEncoderStopped = _STATUSFUNC("getEncoderStopped", C.c_bool, ("encoder", EncoderHandle))
getEncoderDirection = _STATUSFUNC("getEncoderDirection", C.c_bool, ("encoder", EncoderHandle))
getEncoderDistance = _STATUSFUNC("getEncoderDistance", C.c_double, ("encoderHandle", EncoderHandle))
getEncoderRate = _STATUSFUNC("getEncoderRate", C.c_double, ("encoderHandle", EncoderHandle))
setEncoderMinRate = _STATUSFUNC("setEncoderMinRate", None, ("encoderHandle", EncoderHandle), ("minRate", C.c_double))
setEncoderDistancePerPulse = _STATUSFUNC("setEncoderDistancePerPulse", None, ("encoderHandle", EncoderHandle), ("distancePerPulse", C.c_double))
setEncoderReverseDirection = _STATUSFUNC("setEncoderReverseDirection", None, ("encoder", EncoderHandle), ("reverse_direction", C.c_bool))
setEncoderSamplesToAverage = _STATUSFUNC("setEncoderSamplesToAverage", None, ("encoder", EncoderHandle), ("samples_to_average", C.c_int32))
getEncoderSamplesToAverage = _STATUSFUNC("getEncoderSamplesToAverage", C.c_int32, ("encoder", EncoderHandle))
setEncoderIndexSource = _STATUSFUNC("setEncoderIndexSource", None, ("encoderHandle", EncoderHandle), ("digitalSourceHandle", Handle), ("analogTriggerType", C.c_int32), ("type", C.c_int32))
getEncoderFPGAIndex = _STATUSFUNC("getEncoderFPGAIndex", C.c_int32, ("encoderHandle", EncoderHandle))
getEncoderDecodingScaleFactor = _STATUSFUNC("getEncoderDecodingScaleFactor", C.c_double, ("encoderHandle", EncoderHandle))
getEncoderDistancePerPulse = _STATUSFUNC("getEncoderDistancePerPulse", C.c_double, ("encoderHandle", EncoderHandle))
getEncoderEncodingType = _STATUSFUNC("getEncoderEncodingType", C.c_int32, ("encoderHandle", EncoderHandle))


#############################################################################
# I2C
#############################################################################

initializeI2C = _TSTATUSFUNC("initializeI2C", None, ("port", C.c_int32))

_transactionI2C = _THUNKFUNC("transactionI2C", C.c_int32, ("port", C.c_int32), ("deviceAddress", C.c_int32),
                           ("dataToSend", C.POINTER(C.c_uint8)), ("sendSize", C.c_int32),
                           ("dataReceived", C.POINTER(C.c_uint8)), ("receiveSize", C.c_int32))
@hal_wrapper
def transactionI2C(port, deviceAddress, dataToSend, receiveSize):
    sendSize = len(dataToSend)
    send_buffer = (C.c_uint8 * sendSize)(*dataToSend)
    recv_buffer = (C.c_uint8 * receiveSize)()
    rv = _transactionI2C(port, deviceAddress, send_buffer, sendSize, recv_buffer, receiveSize)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return recv_buffer[:]

_writeI2C = _THUNKFUNC("writeI2C", C.c_int32, ("port", C.c_int32), ("deviceAddress", C.c_int32),
                       ("dataToSend", C.POINTER(C.c_uint8)), ("sendSize", C.c_int32))
@hal_wrapper
def writeI2C(port, deviceAddress, dataToSend):
    sendSize = len(dataToSend)
    buffer = (C.c_uint8 * sendSize)(*dataToSend)
    rv = _writeI2C(port, deviceAddress, buffer, sendSize)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))

_readI2C = _THUNKFUNC("readI2C", C.c_int32, ("port", C.c_int32), ("deviceAddress", C.c_int32),
                     ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_int32))
@hal_wrapper
def readI2C(port, deviceAddress, count):
    buffer = (C.c_uint8 * count)()
    rv = _readI2C(port, deviceAddress, buffer, count)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return buffer[:]

closeI2C = _THUNKFUNC("closeI2C", None, ("port", C.c_int32))

#############################################################################
# Interrupts
#############################################################################

_InterruptHandlerFunction = C.CFUNCTYPE(None, C.c_uint32, C.c_void_p)
_InterruptHandlerFunction._typedef_ = 'InterruptHandlerFunction'

_interruptHandlers = {}

initializeInterrupts = _STATUSFUNC("initializeInterrupts", InterruptHandle, ("watcher", C.c_bool))
_cleanInterrupts = _STATUSFUNC("cleanInterrupts", None, ("interrupt", InterruptHandle))
@hal_wrapper
def cleanInterrupts(interrupt):
    _cleanInterrupts(interrupt)

    # remove references to function handlers
    _interruptHandlers.pop(interrupt, None)

waitForInterrupt = _STATUSFUNC("waitForInterrupt", C.c_int64, ("interrupt", InterruptHandle), ("timeout", C.c_double), ("ignorePrevious", C.c_bool))
enableInterrupts = _STATUSFUNC("enableInterrupts", None, ("interrupt", InterruptHandle))
disableInterrupts = _STATUSFUNC("disableInterrupts", None, ("interrupt", InterruptHandle))
readInterruptRisingTimestamp = _STATUSFUNC("readInterruptRisingTimestamp", C.c_double, ("interrupt", InterruptHandle))
readInterruptFallingTimestamp = _STATUSFUNC("readInterruptFallingTimestamp", C.c_double, ("interrupt", InterruptHandle))
requestInterrupts = _STATUSFUNC("requestInterrupts", None, ("interruptHandle", InterruptHandle), ("digitalSourceHandle", Handle), ("analogTriggerType", C.c_int32))
attachInterruptHandlerThreaded = _STATUSFUNC("attachInterruptHandlerThreaded", None, ("interruptHandle", InterruptHandle), ("handler", _InterruptHandlerFunction), ("param", C.POINTER(None)))

_attachInterruptHandler = _STATUSFUNC("attachInterruptHandler", None, ("interrupt", InterruptHandle), ("handler", _InterruptHandlerFunction), ("param", C.c_void_p))
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

setInterruptUpSourceEdge = _STATUSFUNC("setInterruptUpSourceEdge", None, ("interrupt", InterruptHandle), ("rising_edge", C.c_bool), ("falling_edge", C.c_bool))


#############################################################################
# Notifier
#############################################################################

# Not implemented


#############################################################################
# PDP
#############################################################################

initializePDP = _STATUSFUNC("initializePDP", None, ("module", C.c_int32))
checkPDPChannel = _RETFUNC("checkPDPChannel", C.c_bool, ("channel", C.c_int32))
checkPDPModule = _RETFUNC("checkPDPModule", C.c_bool, ("module", C.c_int32))
getPDPTemperature = _STATUSFUNC("getPDPTemperature", C.c_double, ("module", C.c_int32))
getPDPVoltage = _STATUSFUNC("getPDPVoltage", C.c_double, ("module", C.c_int32))
getPDPChannelCurrent = _STATUSFUNC("getPDPChannelCurrent", C.c_double, ("module", C.c_int32), ("channel", C.c_int32))
getPDPTotalCurrent = _STATUSFUNC("getPDPTotalCurrent", C.c_double, ("module", C.c_int32))
getPDPTotalPower = _STATUSFUNC("getPDPTotalPower", C.c_double, ("module", C.c_int32))
getPDPTotalEnergy = _STATUSFUNC("getPDPTotalEnergy", C.c_double, ("module", C.c_int32))
resetPDPTotalEnergy = _STATUSFUNC("resetPDPTotalEnergy", None, ("module", C.c_int32))
clearPDPStickyFaults = _STATUSFUNC("clearPDPStickyFaults", None, ("module", C.c_int32))


#############################################################################
# PWM
#############################################################################

initializePWMPort = _STATUSFUNC("initializePWMPort", DigitalHandle, ("portHandle", PortHandle))
freePWMPort = _STATUSFUNC("freePWMPort", None, ("pwmPortHandle", DigitalHandle))
checkPWMChannel = _RETFUNC("checkPWMChannel", C.c_bool, ("channel", C.c_int32))

setPWMConfig = _STATUSFUNC("setPWMConfig", None, ("pwmPortHandle", DigitalHandle), ("maxPwm", C.c_double), ("deadbandMaxPwm", C.c_double), ("centerPwm", C.c_double), ("deadbandMinPwm", C.c_double), ("minPwm", C.c_double))
setPWMConfigRaw = _STATUSFUNC("setPWMConfigRaw", None, ("pwmPortHandle", DigitalHandle), ("maxPwm", C.c_int32), ("deadbandMaxPwm", C.c_int32), ("centerPwm", C.c_int32), ("deadbandMinPwm", C.c_int32), ("minPwm", C.c_int32))
getPWMConfigRaw = _STATUSFUNC("getPWMConfigRaw", None, ("pwmPortHandle", DigitalHandle), ("maxPwm", C.POINTER(C.c_int32)), ("deadbandMaxPwm", C.POINTER(C.c_int32)), ("centerPwm", C.POINTER(C.c_int32)), ("deadbandMinPwm", C.POINTER(C.c_int32)), ("minPwm", C.POINTER(C.c_int32)), out=["maxPwm", "deadbandMaxPwm", "centerPwm", "deadbandMinPwm", "minPwm"])
setPWMEliminateDeadband = _STATUSFUNC("setPWMEliminateDeadband", None, ("pwmPortHandle", DigitalHandle), ("eliminateDeadband", C.c_bool))
getPWMEliminateDeadband = _STATUSFUNC("getPWMEliminateDeadband", C.c_bool, ("pwmPortHandle", DigitalHandle))

setPWMRaw = _STATUSFUNC("setPWMRaw", None, ("pwmPortHandle", DigitalHandle), ("value", C.c_int32))
setPWMSpeed = _STATUSFUNC("setPWMSpeed", None, ("pwmPortHandle", DigitalHandle), ("speed", C.c_double))
setPWMPosition = _STATUSFUNC("setPWMPosition", None, ("pwmPortHandle", DigitalHandle), ("position", C.c_double))
setPWMDisabled = _STATUSFUNC("setPWMDisabled", None, ("pwmPortHandle", DigitalHandle))
getPWMRaw = _STATUSFUNC("getPWMRaw", C.c_int32, ("pwmPortHandle", DigitalHandle))
getPWMSpeed = _STATUSFUNC("getPWMSpeed", C.c_double, ("pwmPortHandle", DigitalHandle))
getPWMPosition = _STATUSFUNC("getPWMPosition", C.c_double, ("pwmPortHandle", DigitalHandle))

latchPWMZero = _STATUSFUNC("latchPWMZero", None, ("pwmPortHandle", DigitalHandle))
setPWMPeriodScale = _STATUSFUNC("setPWMPeriodScale", None, ("pwmPortHandle", DigitalHandle), ("squelchMask", C.c_int32))
getLoopTiming = _STATUSFUNC("getLoopTiming", C.c_int32)

#############################################################################
# Ports
#############################################################################

getNumAccumulators = _RETFUNC("getNumAccumulators", C.c_int32)
getNumAnalogTriggers = _RETFUNC("getNumAnalogTriggers", C.c_int32)
getNumAnalogInputs = _RETFUNC("getNumAnalogInputs", C.c_int32)
getNumAnalogOutputs = _RETFUNC("getNumAnalogOutputs", C.c_int32)
getNumCounters = _RETFUNC("getNumCounters", C.c_int32)
getNumDigitalHeaders = _RETFUNC("getNumDigitalHeaders", C.c_int32)
getNumPWMHeaders = _RETFUNC("getNumPWMHeaders", C.c_int32)
getNumDigitalChannels = _RETFUNC("getNumDigitalChannels", C.c_int32)
getNumPWMChannels = _RETFUNC("getNumPWMChannels", C.c_int32)
getNumDigitalPWMOutputs = _RETFUNC("getNumDigitalPWMOutputs", C.c_int32)
getNumEncoders = _RETFUNC("getNumEncoders", C.c_int32)
getNumInterrupts = _RETFUNC("getNumInterrupts", C.c_int32)
getNumRelayChannels = _RETFUNC("getNumRelayChannels", C.c_int32)
getNumRelayHeaders = _RETFUNC("getNumRelayHeaders", C.c_int32)
getNumPCMModules = _RETFUNC("getNumPCMModules", C.c_int32)
getNumSolenoidChannels = _RETFUNC("getNumSolenoidChannels", C.c_int32)
getNumPDPModules = _RETFUNC("getNumPDPModules", C.c_int32)
getNumPDPChannels = _RETFUNC("getNumPDPChannels", C.c_int32)


#############################################################################
# Power
#############################################################################

getVinVoltage = _STATUSFUNC("getVinVoltage", C.c_double)
getVinCurrent = _STATUSFUNC("getVinCurrent", C.c_double)
getUserVoltage6V = _STATUSFUNC("getUserVoltage6V", C.c_double)
getUserCurrent6V = _STATUSFUNC("getUserCurrent6V", C.c_double)
getUserActive6V = _STATUSFUNC("getUserActive6V", C.c_bool)
getUserCurrentFaults6V = _STATUSFUNC("getUserCurrentFaults6V", C.c_int)
getUserVoltage5V = _STATUSFUNC("getUserVoltage5V", C.c_double)
getUserCurrent5V = _STATUSFUNC("getUserCurrent5V", C.c_double)
getUserActive5V = _STATUSFUNC("getUserActive5V", C.c_bool)
getUserCurrentFaults5V = _STATUSFUNC("getUserCurrentFaults5V", C.c_int)
getUserVoltage3V3 = _STATUSFUNC("getUserVoltage3V3", C.c_double)
getUserCurrent3V3 = _STATUSFUNC("getUserCurrent3V3", C.c_double)
getUserActive3V3 = _STATUSFUNC("getUserActive3V3", C.c_bool)
getUserCurrentFaults3V3 = _STATUSFUNC("getUserCurrentFaults3V3", C.c_int)

#############################################################################
# Relay
#############################################################################

initializeRelayPort = _STATUSFUNC("initializeRelayPort", RelayHandle, ("portHandle", PortHandle), ("fwd", C.c_bool))
freeRelayPort = _RETFUNC("freeRelayPort", None, ("relayPortHandle", RelayHandle))
checkRelayChannel = _RETFUNC("checkRelayChannel", C.c_bool, ("channel", C.c_int32))
setRelay = _STATUSFUNC("setRelay", None, ("relayPortHandle", RelayHandle), ("on", C.c_bool))
getRelay = _STATUSFUNC("getRelay", C.c_bool, ("relayPortHandle", RelayHandle))

#############################################################################
# SPI
#############################################################################

initializeSPI = _TSTATUSFUNC("initializeSPI", None, ("port", C.c_int32))

_transactionSPI = _THUNKFUNC("transactionSPI", C.c_int32, ("port", C.c_int32),
                           ("dataToSend", C.POINTER(C.c_uint8)), ("dataReceived", C.POINTER(C.c_uint8)), ("size", C.c_int32))
@hal_wrapper
def transactionSPI(port, dataToSend):
    size = len(dataToSend)
    send_buffer = (C.c_uint8 * size)(*dataToSend)
    recv_buffer = (C.c_uint8 * size)()
    rv = _transactionSPI(port, send_buffer, recv_buffer, size)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return recv_buffer[:rv]

_writeSPI = _THUNKFUNC("writeSPI", C.c_int32, ("port", C.c_int32), ("dataToSend", C.POINTER(C.c_uint8)), ("sendSize", C.c_int32))
@hal_wrapper
def writeSPI(port, dataToSend):
    sendSize = len(dataToSend)
    buffer = (C.c_uint8 * sendSize)(*dataToSend)
    rv = _writeSPI(port, buffer, sendSize)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return rv

_readSPI = _THUNKFUNC("readSPI", C.c_int32, ("port", C.c_int32), ("buffer", C.POINTER(C.c_uint8)), ("count", C.c_int32))
@hal_wrapper
def readSPI(port, count):
    buffer = (C.c_uint8 * count)()
    rv = _readSPI(port, buffer, count)
    if rv < 0:
        raise IOError(_os.strerror(C.get_errno()))
    return buffer[:]

closeSPI = _THUNKFUNC("closeSPI", None, ("port", C.c_int32))
setSPISpeed = _THUNKFUNC("setSPISpeed", None, ("port", C.c_int32), ("speed", C.c_int32))
setSPISpeed = _THUNKFUNC("setSPISpeed", None, ("port", C.c_int32), ("speed", C.c_int32))
setSPIOpts = _THUNKFUNC("setSPIOpts", None, ("port", C.c_int32), ("msbFirst", C.c_bool), ("sampleOnTrailing", C.c_bool), ("clkIdleHigh", C.c_bool))
setSPIChipSelectActiveHigh = _TSTATUSFUNC("setSPIChipSelectActiveHigh", None, ("port", C.c_int32))
setSPIChipSelectActiveLow = _TSTATUSFUNC("setSPIChipSelectActiveLow", None, ("port", C.c_int32))
getSPIHandle = _THUNKFUNC("getSPIHandle", C.c_int32, ("port", C.c_int32))
setSPIHandle = _THUNKFUNC("setSPIHandle", None, ("port", C.c_int32), ("handle", C.c_int32))
initSPIAccumulator = _TSTATUSFUNC("initSPIAccumulator", None, ("port", C.c_int32), ("period", C.c_int32), ("cmd", C.c_int32), ("xferSize", C.c_int32), ("validMask", C.c_int32), ("validValue", C.c_int32), ("dataShift", C.c_int32), ("dataSize", C.c_int32), ("isSigned", C.c_bool), ("bigEndian", C.c_bool))
freeSPIAccumulator = _TSTATUSFUNC("freeSPIAccumulator", None, ("port", C.c_int32))
resetSPIAccumulator = _TSTATUSFUNC("resetSPIAccumulator", None, ("port", C.c_int32))
setSPIAccumulatorCenter = _TSTATUSFUNC("setSPIAccumulatorCenter", None, ("port", C.c_int32), ("center", C.c_int32))
setSPIAccumulatorDeadband = _TSTATUSFUNC("setSPIAccumulatorDeadband", None, ("port", C.c_int32), ("deadband", C.c_int32))
getSPIAccumulatorLastValue = _TSTATUSFUNC("getSPIAccumulatorLastValue", C.c_int32, ("port", C.c_int32))
getSPIAccumulatorValue = _TSTATUSFUNC("getSPIAccumulatorValue", C.c_int64, ("port", C.c_int32))
getSPIAccumulatorCount = _TSTATUSFUNC("getSPIAccumulatorCount", C.c_int64, ("port", C.c_int32))
getSPIAccumulatorAverage = _TSTATUSFUNC("getSPIAccumulatorAverage", C.c_double, ("port", C.c_int32))
getSPIAccumulatorOutput = _TSTATUSFUNC("getSPIAccumulatorOutput", None, ("port", C.c_int32), ("value", C.POINTER(C.c_int64)), ("count", C.POINTER(C.c_int64)), out=["value", "count"])


#############################################################################
# Solenoid
#############################################################################

initializeSolenoidPort = _STATUSFUNC("initializeSolenoidPort", SolenoidHandle, ("port", PortHandle))
freeSolenoidPort = _RETFUNC('freeSolenoidPort', None, ('port', SolenoidHandle))
checkSolenoidModule = _RETFUNC("checkSolenoidModule", C.c_bool, ("module", C.c_int32))
checkSolenoidChannel = _RETFUNC("checkSolenoidChannel", C.c_bool, ("channel", C.c_int32))

getSolenoid = _STATUSFUNC("getSolenoid", C.c_bool, ("solenoid_port", SolenoidHandle))
getAllSolenoids = _STATUSFUNC("getAllSolenoids", C.c_int32, ("module", C.c_int32))
setSolenoid = _STATUSFUNC("setSolenoid", None, ("solenoid_port", SolenoidHandle), ("value", C.c_bool))

getPCMSolenoidBlackList = _STATUSFUNC("getPCMSolenoidBlackList", C.c_int, ("module", C.c_int32))
getPCMSolenoidVoltageStickyFault = _STATUSFUNC("getPCMSolenoidVoltageStickyFault", C.c_bool, ("module", C.c_int32))
getPCMSolenoidVoltageFault = _STATUSFUNC("getPCMSolenoidVoltageFault", C.c_bool, ("module", C.c_int32))
clearAllPCMStickyFaults = _STATUSFUNC("clearAllPCMStickyFaults", None, ("module", C.c_int32))
