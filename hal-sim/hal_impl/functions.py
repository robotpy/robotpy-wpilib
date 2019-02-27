import logging
import operator

import _hal_constants as constants
from . import data
from . import types
from .data import hal_data, NotifyDict
from .sim_hooks import SimHooks

logger = logging.getLogger("hal")

hooks = SimHooks()

_initialized = False


def reset_hal():
    data._reset_hal_data(hooks)
    globals()["_initialized"] = False
    initialize()


#
# Misc constants
#

CTR_RxTimeout = 1
CTR_TxTimeout = 2
CTR_InvalidParamValue = 3
CTR_UnexpectedArbId = 4
CTR_TxFailed = 5
CTR_SigNotUpdated = 6

NiFpga_Status_FifoTimeout = -50400
NiFpga_Status_TransferAborted = -50405
NiFpga_Status_MemoryFull = -52000
NiFpga_Status_SoftwareFault = -52003
NiFpga_Status_InvalidParameter = -52005
NiFpga_Status_ResourceNotFound = -52006
NiFpga_Status_ResourceNotInitialized = -52010
NiFpga_Status_HardwareFault = -52018
NiFpga_Status_IrqTimeout = -61060

ERR_CANSessionMux_InvalidBuffer = -44408
ERR_CANSessionMux_MessageNotFound = -44087
WARN_CANSessionMux_NoToken = 44087
ERR_CANSessionMux_NotAllowed = -44088
ERR_CANSessionMux_NotInitialized = -44089

SAMPLE_RATE_TOO_HIGH = 1001
VOLTAGE_OUT_OF_RANGE = 1002
LOOP_TIMING_ERROR = 1004
SPI_WRITE_NO_MOSI = 1012
SPI_READ_NO_MISO = 1013
SPI_READ_NO_DATA = 1014
INCOMPATIBLE_STATE = 1015
NO_AVAILABLE_RESOURCES = -1004
NULL_PARAMETER = -1005
ANALOG_TRIGGER_LIMIT_ORDER_ERROR = -1010
ANALOG_TRIGGER_PULSE_OUTPUT_ERROR = -1011
PARAMETER_OUT_OF_RANGE = -1028
RESOURCE_IS_ALLOCATED = -1029
RESOURCE_OUT_OF_RANGE = -1030
HAL_INVALID_ACCUMULATOR_CHANNEL = -1035
HAL_COUNTER_NOT_SUPPORTED = -1058
HAL_PWM_SCALE_ERROR = -1072
HAL_HANDLE_ERROR = -1098

#############################################################################
# ConstantsInternal.h
#############################################################################
kSystemClockTicksPerMicrosecond = 40

#############################################################################
# PortsInternal.h
#############################################################################

kNumAccumulators = 2
kNumAnalogTriggers = 8
kNumAnalogInputs = 8
kNumAnalogOutputs = 2  # mxp only
kNumCounters = 8
kNumDigitalHeaders = 10
kNumDigitalMXPChannels = 16
kNumDigitalSPIPortChannels = 5
kNumPWMHeaders = 10
kNumDigitalChannels = (
    kNumDigitalHeaders + kNumDigitalMXPChannels + kNumDigitalSPIPortChannels
)
kNumPWMChannels = 10 + kNumPWMHeaders
kNumDigitalPWMOutputs = 4 + 2
kNumEncoders = 8
kNumInterrupts = 8
kNumRelayChannels = 8
kNumRelayHeaders = int(kNumRelayChannels / 2)
kNumPCMModules = 63
kNumSolenoidChannels = 8
kNumPDPModules = 63
kNumPDPChannels = 16

kAccumulatorChannels = [0, 1]


def _initport(name, idx, status, root=hal_data):
    try:
        if idx < 0:
            raise IndexError()

        data = root[name][idx]
    except IndexError:
        status.value = PARAMETER_OUT_OF_RANGE
        return

    if data["initialized"]:
        status.value = RESOURCE_IS_ALLOCATED
        return

    data["initialized"] = True
    status.value = 0
    return data


#############################################################################
# HAL
#############################################################################


def sleep(s):
    hooks.delaySeconds(s)


def getPort(channel):
    return getPortWithModule(0, channel)


def getPortWithModule(module, channel):
    return types.PortHandle(channel, module)


def _getErrorMessage(code):
    if code == 0:
        return ""

    elif code == CTR_RxTimeout:
        return "CTRE CAN Recieve Timeout"
    elif code == CTR_InvalidParamValue:
        return "CTRE CAN Invalid Parameter"
    elif code == CTR_UnexpectedArbId:
        return "CTRE Unexpected Arbitration ID (CAN Node ID)"
    elif code == CTR_TxFailed:
        return "CTRE CAN Transmit Error"
    elif code == CTR_SigNotUpdated:
        return "CTRE CAN Signal Not Updated"
    elif code == NiFpga_Status_FifoTimeout:
        return "NIFPGA: FIFO timeout error"
    elif code == NiFpga_Status_TransferAborted:
        return "NIFPGA: Transfer aborted error"
    elif code == NiFpga_Status_MemoryFull:
        return "NIFPGA: Memory Allocation failed, memory full"
    elif code == NiFpga_Status_SoftwareFault:
        return "NIFPGA: Unexepected software error"
    elif code == NiFpga_Status_InvalidParameter:
        return "NIFPGA: Invalid Parameter"
    elif code == NiFpga_Status_ResourceNotFound:
        return "NIFPGA: Resource not found"
    elif code == NiFpga_Status_ResourceNotInitialized:
        return "NIFPGA: Resource not initialized"
    elif code == NiFpga_Status_HardwareFault:
        return "NIFPGA: Hardware Fault"
    elif code == NiFpga_Status_IrqTimeout:
        return "NIFPGA: Interrupt timeout"

    elif code == ERR_CANSessionMux_InvalidBuffer:
        return "CAN: Invalid Buffer"
    elif code == ERR_CANSessionMux_MessageNotFound:
        return "CAN: Message not found"
    elif code == WARN_CANSessionMux_NoToken:
        return "CAN: No token"
    elif code == ERR_CANSessionMux_NotAllowed:
        return "CAN: Not allowed"
    elif code == ERR_CANSessionMux_NotInitialized:
        return "CAN: Not initialized"

    elif code == SAMPLE_RATE_TOO_HIGH:
        return "HAL: Analog module sample rate is too high"
    elif code == VOLTAGE_OUT_OF_RANGE:
        return "HAL: Voltage to convert to raw value is out of range [0; 5]"
    elif code == LOOP_TIMING_ERROR:
        return "HAL: Digital module loop timing is not the expected value"
    elif code == SPI_WRITE_NO_MOSI:
        return "HAL: Cannot write to SPI port with no MOSI output"
    elif code == SPI_READ_NO_MISO:
        return "HAL: Cannot read from SPI port with no MISO input"
    elif code == SPI_READ_NO_DATA:
        return "HAL: No data available to read from SPI"
    elif code == INCOMPATIBLE_STATE:
        return "HAL: Incompatible State: The operation cannot be completed"
    elif code == NO_AVAILABLE_RESOURCES:
        return "HAL: No available resources to allocate"
    elif code == NULL_PARAMETER:
        return "HAL: A pointer parameter to a method is NULL"
    elif code == ANALOG_TRIGGER_LIMIT_ORDER_ERROR:
        return "HAL: AnalogTrigger limits error.  Lower limit > Upper Limit"
    elif code == ANALOG_TRIGGER_PULSE_OUTPUT_ERROR:
        return "HAL: Attempted to read AnalogTrigger pulse output."
    elif code == PARAMETER_OUT_OF_RANGE:
        return "HAL: A parameter is out of range."
    elif code == RESOURCE_IS_ALLOCATED:
        return "HAL: A resource is already allocated."
    elif code == RESOURCE_OUT_OF_RANGE:
        return "HAL: The requested resource is out of range."
    elif code == HAL_INVALID_ACCUMULATOR_CHANNEL:
        return "HAL: The requested input is not an accumulator channel"
    elif code == HAL_COUNTER_NOT_SUPPORTED:
        return "HAL: Counter mode not supported for encoder method"
    elif code == HAL_PWM_SCALE_ERROR:
        return "HAL: The PWM Scale Factors are out of range"
    elif code == HAL_HANDLE_ERROR:
        return "HAL: A handle parameter was passed incorrectly"
    else:
        return "Unknown error status %s" % code


def getErrorMessage(code):
    return bytes(_getErrorMessage(code), "utf-8")


def getFPGAVersion(status):
    status.value = 0
    return 2018


def getFPGARevision(status):
    status.value = 0
    return 0


def getFPGATime(status):
    status.value = 0
    return hooks.getFPGATime()


def getRuntimeType():
    return constants.RuntimeType.Mock


def getFPGAButton(status):
    status.value = 0
    return hal_data["fpga_button"]


def getSystemActive(status):
    status.value = 0
    return True


def getBrownedOut(status):
    status.value = 0
    return False


def baseInitialize(status):
    global _initialized
    if _initialized:
        return
    _initialized = True


def initialize(timeout=0, mode=0):
    global _initialized
    if _initialized:
        return
    baseInitialize(None)
    # initializeNotifier()
    initializeDriverStation()

    return True


def report(resource, instanceNumber, context=0, feature=None):

    # TODO: Cover all interesting devices
    hur = constants.HALUsageReporting
    if resource == hur.kResourceType_Jaguar:
        hal_data["pwm"][instanceNumber]["type"] = "jaguar"
    elif resource == hur.kResourceType_MindsensorsSD540:
        hal_data["pwm"][instanceNumber]["type"] = "sd540"
    elif resource == hur.kResourceType_RevSPARK:
        hal_data["pwm"][instanceNumber]["type"] = "spark"
    elif resource == hur.kResourceType_Talon:
        hal_data["pwm"][instanceNumber]["type"] = "talon"
    elif resource == hur.kResourceType_PWMTalonSRX:
        hal_data["pwm"][instanceNumber]["type"] = "pwmtalonsrx"
    elif resource == hur.kResourceType_Victor:
        hal_data["pwm"][instanceNumber]["type"] = "victor"
    elif resource == hur.kResourceType_VictorSP:
        hal_data["pwm"][instanceNumber]["type"] = "victorsp"
    elif resource == hur.kResourceType_PWMVictorSPX:
        hal_data["pwm"][instanceNumber]["type"] = "pwmvictorspx"
    elif resource == hur.kResourceType_DigilentDMC60:
        hal_data["pwm"][instanceNumber]["type"] = "dmc60"

    hal_data["reports"].setdefault(resource, []).append(instanceNumber)
    return 0


#############################################################################
# Accelerometer.h
#############################################################################


def setAccelerometerActive(active):
    hal_data["accelerometer"]["active"] = active


def setAccelerometerRange(range):
    hal_data["accelerometer"]["range"] = range


def getAccelerometerX():
    return hal_data["accelerometer"]["x"]


def getAccelerometerY():
    return hal_data["accelerometer"]["y"]


def getAccelerometerZ():
    return hal_data["accelerometer"]["z"]


#############################################################################
# AnalogAccumulator.h
#############################################################################


def isAccumulatorChannel(analogPortHandle, status):
    status.value = 0
    return analogPortHandle.pin in kAccumulatorChannels


def initAccumulator(analogPortHandle, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_initialized"] = True


def resetAccumulator(analogPortHandle, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_center"] = 0
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_count"] = 1
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_value"] = 0


def setAccumulatorCenter(analogPortHandle, center, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_center"] = center


def setAccumulatorDeadband(analogPortHandle, deadband, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["accumulator_deadband"] = deadband


def getAccumulatorValue(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["accumulator_value"]


def getAccumulatorCount(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["accumulator_count"]


def getAccumulatorOutput(analogPortHandle, status):
    status.value = 0
    return (
        hal_data["analog_in"][analogPortHandle.pin]["accumulator_value"],
        hal_data["analog_in"][analogPortHandle.pin]["accumulator_count"],
    )


#############################################################################
# AnalogGyro.h
#############################################################################


def initializeAnalogGyro(handle, status):
    handle = types.GyroHandle(handle)

    data = _initport("analog_gyro", handle.pin, status)
    if not data:
        return

    data["offset"] = 0
    data["deadband"] = 0
    data["volts_per_degree"] = 0

    data["angle"] = 0
    data["rate"] = 0

    return handle


def setupAnalogGyro(handle, status):
    status.value = 0
    assert hal_data["analog_gyro"][handle.pin]["initialized"]


def freeAnalogGyro(handle):
    hal_data["analog_gyro"][handle.pin]["initialized"] = False


def setAnalogGyroParameters(handle, voltsPerDegreePerSecond, offset, center, status):
    status.value = 0
    data = hal_data["analog_gyro"][handle.pin]
    data["volts_per_degree"] = voltsPerDegreePerSecond
    data["offset"] = offset
    data["center"] = center


def setAnalogGyroVoltsPerDegreePerSecond(handle, voltsPerDegreePerSecond, status):
    status.value = 0
    hal_data["analog_gyro"][handle.pin]["volts_per_degree"] = voltsPerDegreePerSecond


def resetAnalogGyro(handle, status):
    status.value = 0
    data = hal_data["analog_gyro"][handle.pin]
    data["rate"] = 0.0
    data["angle"] = 0.0


def calibrateAnalogGyro(handle, status):
    status.value = 0
    assert hal_data["analog_gyro"][handle.pin]["initialized"]


def setAnalogGyroDeadband(handle, volts, status):
    status.value = 0
    hal_data["analog_gyro"][handle.pin]["deadband"] = volts


def getAnalogGyroAngle(handle, status):
    status.value = 0
    return hal_data["analog_gyro"][handle.pin]["angle"]


def getAnalogGyroRate(handle, status):
    status.value = 0
    return hal_data["analog_gyro"][handle.pin]["rate"]


def getAnalogGyroOffset(handle, status):
    status.value = 0
    return hal_data["analog_gyro"][handle.pin]["offset"]


def getAnalogGyroCenter(handle, status):
    status.value = 0
    return hal_data["analog_gyro"][handle.pin]["center"]


#############################################################################
# AnalogInput.h
#############################################################################


def initializeAnalogInputPort(portHandle, status):
    if _initport("analog_in", portHandle.pin, status):
        return types.AnalogInputHandle(portHandle)


def freeAnalogInputPort(analogPortHandle):
    hal_data["analog_in"][analogPortHandle.pin]["initialized"] = False


def checkAnalogModule(module):
    return module == 1


def checkAnalogInputChannel(channel):
    return channel < kNumAnalogInputs and channel >= 0


def setAnalogSampleRate(samplesPerSecond, status):
    status.value = 0
    hal_data["analog_sample_rate"] = samplesPerSecond


def getAnalogSampleRate(status):
    status.value = 0
    return hal_data["analog_sample_rate"]


def setAnalogAverageBits(analogPortHandle, bits, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["avg_bits"] = bits


def getAnalogAverageBits(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["avg_bits"]


def setAnalogOversampleBits(analogPortHandle, bits, status):
    status.value = 0
    hal_data["analog_in"][analogPortHandle.pin]["oversample_bits"] = bits


def getAnalogOversampleBits(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["oversample_bits"]


def getAnalogValue(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["value"]


def getAnalogAverageValue(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["avg_value"]


def getAnalogVoltsToValue(analogPortHandle, voltage, status):
    status.value = 0
    if voltage > 5.0:
        voltage = 5.0
        status.value = VOLTAGE_OUT_OF_RANGE
    elif voltage < 0.0:
        voltage = 0.0
        status.value = VOLTAGE_OUT_OF_RANGE

    LSBWeight = getAnalogLSBWeight(analogPortHandle, status)
    offset = getAnalogOffset(analogPortHandle, status)
    return (int)((voltage + offset * 1.0e-9) / (LSBWeight * 1.0e-9))


def getAnalogVoltage(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["voltage"]


def getAnalogAverageVoltage(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["avg_voltage"]


def getAnalogLSBWeight(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["lsb_weight"]


def getAnalogOffset(analogPortHandle, status):
    status.value = 0
    return hal_data["analog_in"][analogPortHandle.pin]["offset"]


#############################################################################
# AnalogOutput.h
#############################################################################

kTimebase = 40000000  # < 40 MHz clock
kDefaultOversampleBits = 0
kDefaultAverageBits = 7
kDefaultSampleRate = 50000.0


def initializeAnalogOutputPort(portHandle, status):
    if _initport("analog_out", portHandle.pin, status):
        return types.AnalogOutputHandle(portHandle)


def freeAnalogOutputPort(analogOutputHandle):
    hal_data["analog_out"][analogOutputHandle.pin]["initialized"] = False


def setAnalogOutput(analogOutputHandle, voltage, status):
    status.value = 0
    hal_data["analog_out"][analogOutputHandle.pin]["output"] = voltage


def getAnalogOutput(analogOutputHandle, status):
    status.value = 0
    return hal_data["analog_out"][analogOutputHandle.pin]["output"]


def checkAnalogOutputChannel(channel):
    return channel < kNumAnalogOutputs and channel >= 0


#############################################################################
# AnalogTrigger.h
#############################################################################


def initializeAnalogTrigger(portHandle, status):
    status.value = 0
    for idx in range(0, len(hal_data["analog_trigger"])):
        cnt = hal_data["analog_trigger"][idx]
        if cnt["initialized"] == False:
            cnt["initialized"] = True
            cnt["port"] = portHandle
            return types.AnalogTriggerHandle(portHandle, idx), idx

    status.value = NO_AVAILABLE_RESOURCES
    return None, -1


def cleanAnalogTrigger(analogTriggerHandle, status):
    status.value = 0
    hal_data["analog_trigger"][analogTriggerHandle.index]["initialized"] = False


def setAnalogTriggerLimitsRaw(analogTriggerHandle, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR
    else:
        status.value = 0
        hal_data["analog_trigger"][analogTriggerHandle.index]["trig_lower"] = lower
        hal_data["analog_trigger"][analogTriggerHandle.index]["trig_upper"] = upper


def setAnalogTriggerLimitsVoltage(analogTriggerHandle, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR
    else:
        status.value = 0
        analogPortHandle = hal_data["analog_port"][analogTriggerHandle.pin]
        hal_data["analog_trigger"][analogTriggerHandle.index][
            "trig_lower"
        ] = getAnalogVoltsToValue(analogPortHandle, lower, status)
        hal_data["analog_trigger"][analogTriggerHandle.index][
            "trig_upper"
        ] = getAnalogVoltsToValue(analogPortHandle, upper, status)


def setAnalogTriggerAveraged(analogTriggerHandle, useAveragedValue, status):
    if hal_data["analog_trigger"][analogTriggerHandle.index]["trig_type"] == "filtered":
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0
        hal_data["analog_trigger"][analogTriggerHandle.index]["trig_type"] = (
            "averaged" if useAveragedValue else None
        )


def setAnalogTriggerFiltered(analogTriggerHandle, useFilteredValue, status):
    if hal_data["analog_trigger"][analogTriggerHandle.index]["trig_type"] == "averaged":
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0
        hal_data["analog_trigger"][analogTriggerHandle.index]["trig_type"] = (
            "filtered" if useFilteredValue else None
        )


def _get_trigger_value(analogTriggerHandle):
    ain = hal_data["analog_in"][analogTriggerHandle.pin]
    atr = hal_data["analog_trigger"][analogTriggerHandle.index]
    trig_type = atr["trig_type"]
    if trig_type is None:
        return atr, ain["value"]
    if trig_type == "averaged":
        return atr, ain["avg_value"]
    if trig_type == "filtered":
        return atr, ain["value"]  # XXX
    raise NotImplementedError("Not implemented in simulation")


def getAnalogTriggerInWindow(analogTriggerHandle, status):
    status.value = 0
    atr, val = _get_trigger_value(analogTriggerHandle)
    return val >= atr["trig_lower"] and val <= atr["trig_upper"]


def getAnalogTriggerTriggerState(analogTriggerHandle, status):
    # To work properly, this needs some other runtime component managing the
    # state variable too, but this works well enough
    status.value = 0
    atr, val = _get_trigger_value(analogTriggerHandle)
    if val < atr["trig_lower"]:
        atr["trig_state"] = False
        return False
    elif val > atr["trig_upper"]:
        atr["trig_state"] = True
        return True
    else:
        return atr["trig_state"]


def getAnalogTriggerOutput(analogTriggerHandle, type, status):
    if type == constants.AnalogTriggerType.kInWindow:
        return getAnalogTriggerInWindow(analogTriggerHandle, status)
    if type == constants.AnalogTriggerType.kState:
        return getAnalogTriggerTriggerState(analogTriggerHandle, status)
    else:
        status.value = ANALOG_TRIGGER_PULSE_OUTPUT_ERROR
        return False


#############################################################################
# CAN.h
#############################################################################


def CAN_SendMessage(
    messageID: int, data: bytes, dataSize: int, periodMs: int, status
) -> None:
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def CAN_ReceiveMessage(messageIDMask: int, data: bytearray, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def CAN_OpenStreamSession(
    messageID: int, messageIDMask: int, maxMessages: int, status
) -> int:
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def CAN_CloseStreamSession(sessionHandle: int) -> None:
    pass


def CAN_ReadStreamSession(sessionHandle, messages, messagesToRead, status):
    status.value = 0
    return 0


def CAN_GetCANStatus(status):
    status.value = 0
    return 0.0, 0, 0, 0, 0


#############################################################################
# CANAPI.h
#############################################################################


def initializeCAN(manufacturer, deviceId, deviceType, status) -> types.CANHandle:
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def cleanCAN(handle: types.CANHandle) -> None:
    pass


def writeCANPacket(handle, data, length, apiId, status) -> None:
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def writeCANPacketRepeating(handle, data, length, apiId, repeatMs, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def stopCANPacketRepeating(handle: types.CANHandle, apiId: int, status) -> None:
    status.value = 0
    ...


def readCANPacketNew(handle, apiId, data, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def readCANPacketLatest(handle, apiId, data, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def readCANPacketTimeout(handle, apiId, data, timeoutMs, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def readCANPeriodicPacket(handle, apiId, data, timeoutMs, periodMs, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# Compressor.h
#############################################################################


def initializeCompressor(module, status):
    status.value = 0
    assert module == 0  # don't support multiple modules for now

    hal_data["compressor"]["initialized"] = True
    return types.CompressorHandle(module)


def checkCompressorModule(module):
    return module < 63


def getCompressor(compressorHandle, status):
    status.value = 0
    return hal_data["compressor"]["on"]


def setCompressorClosedLoopControl(compressorHandle, value, status):
    status.value = 0
    hal_data["compressor"]["closed_loop_enabled"] = value


def getCompressorClosedLoopControl(compressorHandle, status):
    status.value = 0
    return hal_data["compressor"]["closed_loop_enabled"]


def getCompressorPressureSwitch(compressorHandle, status):
    status.value = 0
    return hal_data["compressor"]["pressure_switch"]


def getCompressorCurrent(compressorHandle, status):
    status.value = 0
    return hal_data["compressor"]["current"]


def getCompressorCurrentTooHighFault(compressorHandle, status):
    status.value = 0
    return False


def getCompressorCurrentTooHighStickyFault(compressorHandle, status):
    status.value = 0
    return False


def getCompressorShortedFault(compressorHandle, status):
    status.value = 0
    return False


def getCompressorShortedStickyFault(compressorHandle, status):
    status.value = 0
    return False


def getCompressorNotConnectedFault(compressorHandle, status):
    status.value = 0
    return False


def getCompressorNotConnectedStickyFault(compressorHandle, status):
    status.value = 0
    return False


#############################################################################
# Constants.h
#############################################################################


def getSystemClockTicksPerMicrosecond():
    return kSystemClockTicksPerMicrosecond


#############################################################################
# Counter.h
#############################################################################


def initializeCounter(mode, status):
    status.value = 0
    for idx in range(0, len(hal_data["counter"])):
        cnt = hal_data["counter"][idx]
        if cnt["initialized"] == False:
            cnt["initialized"] = True
            cnt["mode"] = mode
            return types.CounterHandle(idx), idx

    status.value = NO_AVAILABLE_RESOURCES
    return None, -1


def freeCounter(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["initialized"] = False


def setCounterAverageSize(counterHandle, size, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["average_size"] = size


def setCounterUpSource(counterHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    # AnalogInputs should be referred to by index, not pin
    try:
        hal_data["counter"][counterHandle.idx][
            "up_source_channel"
        ] = digitalSourceHandle.index
    except AttributeError:
        hal_data["counter"][counterHandle.idx][
            "up_source_channel"
        ] = digitalSourceHandle.pin
    hal_data["counter"][counterHandle.idx]["up_source_trigger"] = analogTriggerType

    if hal_data["counter"][counterHandle.idx]["mode"] in [
        constants.CounterMode.kTwoPulse,
        constants.CounterMode.kExternalDirection,
    ]:
        setCounterUpSourceEdge(counterHandle, True, False, status)


def setCounterUpSourceEdge(counterHandle, risingEdge, fallingEdge, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["up_rising_edge"] = risingEdge
    hal_data["counter"][counterHandle.idx]["up_falling_edge"] = fallingEdge


def clearCounterUpSource(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["up_rising_edge"] = False
    hal_data["counter"][counterHandle.idx]["up_falling_edge"] = False
    hal_data["counter"][counterHandle.idx]["up_source_channel"] = 0
    hal_data["counter"][counterHandle.idx]["up_source_trigger"] = False


def setCounterDownSource(counterHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    if hal_data["counter"][counterHandle.idx]["mode"] not in [
        constants.CounterMode.kTwoPulse,
        constants.CounterMode.kExternalDirection,
    ]:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    # AnalogInputs should be referred to by index, not pin
    try:
        hal_data["counter"][counterHandle.idx][
            "down_source_channel"
        ] = digitalSourceHandle.index
    except AttributeError:
        hal_data["counter"][counterHandle.idx][
            "down_source_channel"
        ] = digitalSourceHandle.pin
    hal_data["counter"][counterHandle.idx]["down_source_trigger"] = analogTriggerType


def setCounterDownSourceEdge(counterHandle, risingEdge, fallingEdge, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["down_rising_edge"] = risingEdge
    hal_data["counter"][counterHandle.idx]["down_falling_edge"] = fallingEdge


def clearCounterDownSource(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["down_rising_edge"] = False
    hal_data["counter"][counterHandle.idx]["down_falling_edge"] = False
    hal_data["counter"][counterHandle.idx]["down_source_channel"] = 0
    hal_data["counter"][counterHandle.idx]["down_source_trigger"] = False


def setCounterUpDownMode(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["mode"] = constants.CounterMode.kTwoPulse


def setCounterExternalDirectionMode(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx][
        "mode"
    ] = constants.CounterMode.kExternalDirection


def setCounterSemiPeriodMode(counterHandle, highSemiPeriod, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["mode"] = constants.CounterMode.kSemiperiod
    hal_data["counter"][counterHandle.idx]["up_rising_edge"] = highSemiPeriod
    hal_data["counter"][counterHandle.idx]["update_when_empty"] = False


def setCounterPulseLengthMode(counterHandle, threshold, status):
    hal_data["counter"][counterHandle.idx]["mode"] = constants.CounterMode.kPulseLength
    hal_data["counter"][counterHandle.idx]["pulse_length_threshold"] = threshold


def getCounterSamplesToAverage(counterHandle, status):
    status.value = 0
    return hal_data["counter"][counterHandle.idx]["samples_to_average"]


def setCounterSamplesToAverage(counterHandle, samplesToAverage, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["samples_to_average"] = samplesToAverage


def resetCounter(counterHandle, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["count"] = 0


def getCounter(counterHandle, status):
    status.value = 0
    return hal_data["counter"][counterHandle.idx]["count"]


def getCounterPeriod(counterHandle, status):
    status.value = 0
    return hal_data["counter"][counterHandle.idx]["period"]


def setCounterMaxPeriod(counterHandle, maxPeriod, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["max_period"] = maxPeriod


def setCounterUpdateWhenEmpty(counterHandle, enabled, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["update_when_empty"] = enabled


def getCounterStopped(counterHandle, status):
    status.value = 0
    cnt = hal_data["counter"][counterHandle.idx]
    return cnt["period"] > cnt["max_period"]


def getCounterDirection(counterHandle, status):
    status.value = 0
    return hal_data["counter"][counterHandle.idx]["direction"]


def setCounterReverseDirection(counterHandle, reverseDirection, status):
    status.value = 0
    hal_data["counter"][counterHandle.idx]["reverse_direction"] = reverseDirection


#############################################################################
# DIO.h
#############################################################################

kExpectedLoopTiming = 40


def _remapMXPChannel(pin):
    return pin - 10


def _remapMXPPWMChannel(pin):
    if pin < 14:
        return pin - 10
    else:
        return pin - 6


def _remapSPIChannel(pin):
    return pin - 26


def initializeDIOPort(portHandle, input, status):
    status.value = 0
    if portHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPChannel(portHandle.pin)
        if hal_data["mxp"][mxp_port]["initialized"]:
            status.value = RESOURCE_IS_ALLOCATED
            return

    dio = _initport("dio", portHandle.pin, status)
    if dio is None:
        return

    if portHandle.pin >= kNumDigitalHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True

    dio["is_input"] = input
    return types.DigitalHandle(portHandle)


def checkDIOChannel(channel):
    return channel < kNumDigitalChannels and channel >= 0


def freeDIOPort(dioPortHandle):
    hal_data["dio"][dioPortHandle.pin]["initialized"] = False
    if dioPortHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPChannel(dioPortHandle.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False
    dioPortHandle.pin = None


def allocateDigitalPWM(status):
    status.value = 0
    handle = 0
    dio = None
    for i, port in enumerate(hal_data["dio"]):
        if i >= kNumDigitalHeaders:
            if not hal_data["mxp"][i]["initialized"]:
                dio = _initport("dio", i, status)
                hal_data["mxp"][i]["initialized"] = True
                handle = i
                break
        if not port["initialized"]:
            dio = _initport("dio", i, status)
            handle = i
            break

    if dio is None:
        status.value = NO_AVAILABLE_RESOURCES
        return None

    return types.DigitalPWMHandle(getPort(handle))


def freeDigitalPWM(pwmGenerator, status):
    status.value = 0
    hal_data["d0_pwm"][pwmGenerator.pin]["pin"] = None


def setDigitalPWMRate(rate, status):
    status.value = 0
    hal_data["d0_pwm_rate"] = rate


def setDigitalPWMDutyCycle(pwmGenerator, dutyCycle, status):
    status.value = 0
    hal_data["d0_pwm"][pwmGenerator.pin]["duty_cycle"] = dutyCycle


def setDigitalPWMOutputChannel(pwmGenerator, channel, status):
    status.value = 0
    hal_data["d0_pwm"][pwmGenerator.pin]["pin"] = channel


def setDIO(dioPortHandle, value, status):
    status.value = 0
    hal_data["dio"][dioPortHandle.pin]["value"] = True if value else False


def setDIODirection(dioPortHandle, input, status):
    status.value = 0
    hal_data["dio"][dioPortHandle.pin]["is_input"] = input


def getDIO(dioPortHandle, status):
    status.value = 0
    return bool(hal_data["dio"][dioPortHandle.pin]["value"])


def getDIODirection(dioPortHandle, status):
    status.value = 0
    return hal_data["dio"][dioPortHandle.pin]["is_input"]


def pulse(dioPortHandle, pulseLength, status):
    status.value = 0
    hal_data["dio"][dioPortHandle.pin]["pulse_length"] = pulseLength


def isPulsing(dioPortHandle, status):
    status.value = 0
    return hal_data["dio"][dioPortHandle.pin]["pulse_length"] is not None


def isAnyPulsing(status):
    status.value = 0

    for p in hal_data["dio"]:
        if p is not None and p["pulse_length"] is not None:
            return True
    return False


def setFilterSelect(dioPortHandle, filterIndex, status):
    if filterIndex < 0 or filterIndex > 3:
        status.value = PARAMETER_OUT_OF_RANGE
        return

    if filterIndex == 0:
        filterIndex = hal_data["dio"][dioPortHandle.pin]["filterIndex"]
        hal_data["dio"][dioPortHandle.pin]["filterIndex"] = None
        hal_data["filter"][filterIndex]["enabled"] = False
    else:
        filterIndex = filterIndex - 1
        hal_data["filter"][filterIndex]["enabled"] = True
        hal_data["dio"][dioPortHandle.pin]["filterIndex"] = filterIndex
    status.value = 0


def getFilterSelect(dioPortHandle, status):
    status.value = 0
    filterIndex = hal_data["dio"][dioPortHandle.pin]["filterIndex"]
    if filterIndex is None:
        return 0
    else:
        return filterIndex + 1  # really?


def setFilterPeriod(filterIndex, value, status):
    if filterIndex < 0 or filterIndex > 2:
        status.value = PARAMETER_OUT_OF_RANGE
        return

    status.value = 0
    hal_data["filter"][filterIndex]["period"] = value


def getFilterPeriod(filterIndex, status):
    if filterIndex < 0 or filterIndex > 2:
        status.value = PARAMETER_OUT_OF_RANGE
        return

    status.value = 0
    return hal_data["filter"][filterIndex]["period"]


#############################################################################
# DriverStation.h
#############################################################################


def setErrorData(errors, errorsLength, waitMs):
    # Nothing calls this anymore
    return 0


def sendError(isError, errorCode, isLVCode, details, location, callStack, printMsg):
    # the only thing that calls this is DriverStation.ReportError
    # and it logs by default now
    hal_data["error_data"] = (isError, details, location)
    return 0


def getControlWord(controlWord):
    controlWord.__dict__.update(hal_data["control"])
    return 0


def getAllianceStation(status):
    status.value = 0
    return hal_data["alliance_station"]


def getJoystickAxes(joystickNum, axes):
    axes.axes = list(map(float, hal_data["joysticks"][joystickNum]["axes"]))
    axes.count = len(axes.axes)
    return 0


def getJoystickPOVs(joystickNum, povs):
    povs.povs = list(map(int, hal_data["joysticks"][joystickNum]["povs"]))
    povs.count = len(povs.povs)
    return 0


def getJoystickButtons(joystickNum, buttons):
    # buttons are stored as booleans for ease of use, convert to integer
    b = hal_data["joysticks"][joystickNum]["buttons"]
    # profiled optimization
    # buttons.buttons = sum(int(v) << i for i, v in enumerate(b[1:]))
    l = len(b) - 1
    buttons.buttons = sum(map(operator.lshift, map(int, b[1:]), range(l)))
    buttons.count = l
    return 0


def getJoystickDescriptor(joystickNum, desc):
    stick = hal_data["joysticks"][joystickNum]
    desc.isXbox = stick["isXbox"]
    desc.type = stick["type"]
    desc.name = stick["name"]
    desc.axisCount = stick["axisCount"]
    desc.buttonCount = stick["buttonCount"]
    return 0


def getJoystickIsXbox(joystickNum):
    return hal_data["joysticks"][joystickNum]["isXbox"]


def getJoystickType(joystickNum):
    return hal_data["joysticks"][joystickNum]["type"]


def getJoystickName(joystickNum):
    name = hal_data["joysticks"][joystickNum]["name"]
    if not isinstance(name, bytes):
        name = bytes(name, "utf-8")
    return name


def freeJoystickName(name):
    pass


def getJoystickAxisType(joystickNum, axis):
    raise NotImplementedError("Not implemented in simulation")


def setJoystickOutputs(joystickNum, outputs, leftRumble, rightRumble):
    hal_data["joysticks"][joystickNum]["leftRumble"] = leftRumble
    hal_data["joysticks"][joystickNum]["rightRumble"] = rightRumble
    hal_data["joysticks"][joystickNum]["outputs"] = [bool(val) for val in bin(outputs)]
    return 0


def getMatchTime(status):
    """
        Returns approximate match time:
        - At beginning of autonomous, time is 0
        - At beginning of teleop, time is set to 15
        - If robot is disabled, time is 0
    """
    status.value = 0
    remaining = hal_data["time"]["remaining"]
    if remaining is None:
        return 135.0
    else:
        return (remaining - hooks.getFPGATime()) / 1000000.0


def getMatchInfo(info):
    evt = hal_data["event"]
    info.eventName = bytes(evt["name"], "utf-8")
    info.matchType = evt["match_type"]
    info.matchNumber = evt["match_number"]
    info.replayNumber = evt["replay_number"]
    info.gameSpecificMessage = bytes(evt["game_specific_message"], "utf-8")
    return 0


def freeMatchInfo(info):
    pass


def releaseDSMutex():
    hooks.notifyDSData()


def isNewControlData():
    return hooks.isNewControlData()


def waitForDSData():
    hooks.waitForDSData()


def waitForDSDataTimeout(timeout):
    return hooks.waitForDSData(timeout)


def initializeDriverStation():
    hooks.initializeDriverStation()


def observeUserProgramStarting():
    hal_data["user_program_state"] = "starting"


def observeUserProgramDisabled():
    hal_data["user_program_state"] = "disabled"


def observeUserProgramAutonomous():
    hal_data["user_program_state"] = "autonomous"


def observeUserProgramTeleop():
    hal_data["user_program_state"] = "teleop"


def observeUserProgramTest():
    hal_data["user_program_state"] = "test"


#############################################################################
# Encoder.h
#############################################################################


def initializeEncoder(
    digitalSourceHandleA,
    analogTriggerTypeA,
    digitalSourceHandleB,
    analogTriggerTypeB,
    reverseDirection,
    encodingType,
    status,
):
    status.value = 0
    for idx in range(0, len(hal_data["encoder"])):
        enc = hal_data["encoder"][idx]
        if enc["initialized"] == False:
            enc["initialized"] = True

            enc["config"] = {
                "ASource_Channel": digitalSourceHandleA.pin,
                "ASource_AnalogTrigger": analogTriggerTypeA,
                "BSource_Channel": digitalSourceHandleB.pin,
                "BSource_AnalogTrigger": analogTriggerTypeB,
            }
            enc["reverse_direction"] = reverseDirection
            return types.EncoderHandle(idx)
    status.value = NO_AVAILABLE_RESOURCES
    return None


def freeEncoder(encoderHandle, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["initialized"] = False


def getEncoder(encoderHandle, status):
    status.value = 0
    return hal_data["encoder"][encoderHandle.idx]["count"]


def getEncoderRaw(encoderHandle, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def getEncoderEncodingScale(encoderHandle, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def resetEncoder(encoderHandle, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["count"] = 0


def getEncoderPeriod(encoderHandle, status):
    status.value = 0
    return hal_data["encoder"][encoderHandle.idx]["period"]


def setEncoderMaxPeriod(encoderHandle, maxPeriod, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["max_period"] = maxPeriod


def getEncoderStopped(encoderHandle, status):
    status.value = 0
    enc = hal_data["encoder"][encoderHandle.idx]
    return enc["period"] > enc["max_period"]


def getEncoderDirection(encoderHandle, status):
    status.value = 0
    return hal_data["encoder"][encoderHandle.idx]["direction"]


def getEncoderDistance(encoderHandle, status):
    status.value = 0
    enc = hal_data["encoder"][encoderHandle.idx]
    return enc["count"] * enc["distance_per_pulse"]


def getEncoderRate(encoderHandle, status):
    status.value = 0
    enc = hal_data["encoder"][encoderHandle.idx]
    return enc["rate"] * enc["distance_per_pulse"]


def setEncoderMinRate(encoderHandle, minRate, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["min_rate"] = minRate


def setEncoderDistancePerPulse(encoderHandle, distancePerPulse, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["distance_per_pulse"] = distancePerPulse


def setEncoderReverseDirection(encoderHandle, reverseDirection, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["reverse_direction"] = reverseDirection


def setEncoderSamplesToAverage(encoderHandle, samplesToAverage, status):
    status.value = 0
    hal_data["encoder"][encoderHandle.idx]["samples_to_average"] = samplesToAverage


def getEncoderSamplesToAverage(encoderHandle, status):
    status.value = 0
    return hal_data["encoder"][encoderHandle.idx]["samples_to_average"]


def setEncoderIndexSource(
    encoderHandle, digitalSourceHandle, analogTriggerType, type, status
):
    status.value = 0
    index_conf = {
        "IndexSource_Channel": digitalSourceHandle.pin,
        "IndexSource_AnalogTrigger": analogTriggerType,
        "IndexType": type,
    }
    hal_data["encoder"][encoderHandle.idx]["config"].update(index_conf)


def getEncoderFPGAIndex(encoderHandle, status):
    status.value = 0
    return encoderHandle.idx


def getEncoderDecodingScaleFactor(encoderHandle, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def getEncoderDistancePerPulse(encoderHandle, status):
    status.value = 0
    return hal_data["encoder"][encoderHandle.idx]["distance_per_pulse"]


def getEncoderEncodingType(encoderHandle, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# Extensions.h
#############################################################################


def loadOneExtension(library):
    raise NotImplementedError("Not implemented in simulation")


def loadExtensions():
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# I2C.h
#############################################################################

#
# i2c: These functions should never get called, pass a simPort object
#      to the i2c implementation instead. See i2c_helpers.py for an
#      example.
#
#      The simPort object should implement all of the i2c functions below
#
# TODO: change WPILib HAL impl to take an object, then we can implement
#       the simport stuff at the HAL layer instead
#


def initializeI2C(port, status):
    raise NotImplementedError("Not implemented in simulation")


def transactionI2C(
    port, deviceAddress, dataToSend, sendSize, dataReceived, receiveSize
):
    raise NotImplementedError("Not implemented in simulation")


def writeI2C(port, deviceAddress, dataToSend, sendSize):
    raise NotImplementedError("Not implemented in simulation")


def readI2C(port, deviceAddress, buffer, count):
    raise NotImplementedError("Not implemented in simulation")


def closeI2C(port):
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# Interrupts
#############################################################################


def initializeInterrupts(watcher, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def cleanInterrupts(interruptHandle, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def waitForInterrupt(interruptHandle, timeout, ignorePrevious, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def enableInterrupts(interruptHandle, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def disableInterrupts(interruptHandle, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def readInterruptRisingTimestamp(interruptHandle, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def readInterruptFallingTimestamp(interruptHandle, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def requestInterrupts(interruptHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def attachInterruptHandler(interruptHandle, handler, param, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


def attachInterruptHandlerThreaded(interruptHandle, handler, param, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setInterruptUpSourceEdge(interruptHandle, risingEdge, fallingEdge, status):
    raise NotImplementedError("Not implemented in simulation")  # TODO


#############################################################################
# Notifier
#############################################################################


def initializeNotifier(status):
    status.value = 0
    handle = types.NotifierHandle()
    handle.lock = hooks.createCondition()
    return handle


def stopNotifier(notifierHandle, status):
    status.value = 0
    with notifierHandle.lock:
        notifierHandle.active = False
        notifierHandle.running = False
        notifierHandle.lock.notify_all()


def cleanNotifier(notifierHandle, status):
    status.value = 0
    with notifierHandle.lock:
        notifierHandle.active = False
        notifierHandle.running = False
        notifierHandle.lock.notify_all()


def updateNotifierAlarm(notifierHandle, triggerTime, status):
    status.value = 0
    with notifierHandle.lock:
        notifierHandle.waitTime = triggerTime
        notifierHandle.running = True
        notifierHandle.updatedAlarm = True
        notifierHandle.lock.notify_all()


def cancelNotifierAlarm(notifierHandle, status):
    status.value = 0
    with notifierHandle.lock:
        notifierHandle.running = False
        notifierHandle.lock.notify_all()


def waitForNotifierAlarm(notifierHandle, status):
    status.value = 0
    with notifierHandle.lock:
        while notifierHandle.active:
            if not notifierHandle.running:
                # TODO: switch to longer wait once pyfrc is fixed
                # waitTime = 1000.0
                waitTime = 0.010
            else:
                waitTime = max(
                    (notifierHandle.waitTime - hooks.getFPGATime()) * 1e-6, 0
                )

            notifierHandle.updatedAlarm = False

            # TODO: fix pyfrc to make this work with the condition instead
            # notifierHandle.lock.wait(timeout=waitTime)
            try:
                notifierHandle.lock.release()
                hooks.delaySeconds(waitTime)
            finally:
                notifierHandle.lock.acquire()

            if notifierHandle.updatedAlarm:
                notifierHandle.updatedAlarm = False
                continue

            if not notifierHandle.running:
                continue
            if not notifierHandle.active:
                break

            notifierHandle.running = False
            return hooks.getFPGATime()

    return 0


#############################################################################
# PDP
#############################################################################


def initializePDP(module, status):
    status.value = 0
    if not checkPDPModule(module):
        status.value = PARAMETER_OUT_OF_RANGE
        return

    if module not in hal_data["pdp"]:
        hal_data["pdp"][module] = NotifyDict(
            {
                "has_source": False,
                "temperature": 0,
                "voltage": 0,
                "current": [0] * 16,
                "total_current": 0,
                "total_power": 0,
                "total_energy": 0,
            }
        )

    return types.PDPHandle(module)


def cleanPDP(handle):
    pass


def checkPDPChannel(channel):
    return channel < kNumPDPChannels and channel >= 0


def checkPDPModule(module):
    return module < kNumPDPModules and module >= 0


def getPDPTemperature(handle, status):
    status.value = 0
    return hal_data["pdp"][handle.module]["temperature"]


def getPDPVoltage(handle, status):
    status.value = 0
    return hal_data["pdp"][handle.module]["voltage"]


def getPDPChannelCurrent(handle, channel, status):
    status.value = 0
    if channel < 0 or channel >= len(hal_data["pdp"][handle.module]["current"]):
        status.value = CTR_InvalidParamValue
        return 0
    status.value = 0
    return hal_data["pdp"][handle.module]["current"][channel]


def getPDPTotalCurrent(handle, status):
    status.value = 0
    return hal_data["pdp"][handle.module]["total_current"]


def getPDPTotalPower(handle, status):
    status.value = 0
    return hal_data["pdp"][handle.module]["total_power"]


def getPDPTotalEnergy(handle, status):
    status.value = 0
    return hal_data["pdp"][handle.module]["total_energy"]


def resetPDPTotalEnergy(handle, status):
    status.value = 0
    hal_data["pdp"][handle.module]["total_energy"] = 0


def clearPDPStickyFaults(handle, status):
    status.value = 0
    # not sure what to do here??


#############################################################################
# PWM
#############################################################################


def initializePWMPort(portHandle, status):
    status.value = 0

    pwmPortHandle = types.DigitalPWMHandle(portHandle)

    if pwmPortHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPPWMChannel(pwmPortHandle.pin)
        if hal_data["mxp"][mxp_port]["initialized"]:
            status.value = RESOURCE_IS_ALLOCATED
            return

    if _initport("pwm", pwmPortHandle.pin, status) is None:
        return

    if pwmPortHandle.pin >= kNumDigitalHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True

    # Defaults to allow an always valid config.
    setPWMConfig(pwmPortHandle, 2.0, 1.501, 1.5, 1.499, 1.0, status)

    return pwmPortHandle


def freePWMPort(pwmPortHandle, status):
    status.value = 0

    assert hal_data["pwm"][pwmPortHandle.pin]["initialized"]
    hal_data["pwm"][pwmPortHandle.pin]["initialized"] = False
    hal_data["pwm"][pwmPortHandle.pin]["raw_value"] = 0
    hal_data["pwm"][pwmPortHandle.pin]["value"] = 0
    hal_data["pwm"][pwmPortHandle.pin]["period_scale"] = None
    hal_data["pwm"][pwmPortHandle.pin]["zero_latch"] = False
    hal_data["pwm"][pwmPortHandle.pin]["elim_deadband"] = False

    if pwmPortHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPPWMChannel(pwmPortHandle.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False

    pwmPortHandle.pin = None


def checkPWMChannel(channel):
    return channel < kNumPWMChannels and channel >= 0


def setPWMConfig(
    pwmPortHandle, maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status
):
    status.value = 0
    # ignored


def setPWMConfigRaw(
    pwmPortHandle, maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status
):
    status.value = 0
    # ignored


def getPWMConfigRaw(
    pwmPortHandle, status
):  # , maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setPWMEliminateDeadband(pwmPortHandle, eliminateDeadband, status):
    status.value = 0
    hal_data["pwm"][pwmPortHandle.pin]["elim_deadband"] = eliminateDeadband


def getPWMEliminateDeadband(pwmPortHandle, status):
    status.value = 0
    return hal_data["pwm"][pwmPortHandle.pin]["elim_deadband"]


def setPWMRaw(pwmPortHandle, value, status):
    status.value = 0
    hal_data["pwm"][pwmPortHandle.pin]["raw_value"] = value


def setPWMSpeed(pwmPortHandle, speed, status):
    status.value = 0
    speed = min(max(speed, -1.0), 1.0)
    hal_data["pwm"][pwmPortHandle.pin]["value"] = speed


def setPWMPosition(pwmPortHandle, position, status):
    status.value = 0
    position = min(max(position, 0), 1.0)
    hal_data["pwm"][pwmPortHandle.pin]["value"] = position


def setPWMDisabled(pwmPortHandle, status):
    setPWMRaw(pwmPortHandle, 0, status)
    setPWMSpeed(pwmPortHandle, 0, status)
    setPWMPosition(pwmPortHandle, 0, status)


def getPWMRaw(pwmPortHandle, status):
    status.value = 0
    return hal_data["pwm"][pwmPortHandle.pin]["raw_value"]


def getPWMSpeed(pwmPortHandle, status):
    status.value = 0
    return hal_data["pwm"][pwmPortHandle.pin]["value"]


def getPWMPosition(pwmPortHandle, status):
    status.value = 0
    return hal_data["pwm"][pwmPortHandle.pin]["value"]


def latchPWMZero(pwmPortHandle, status):
    # TODO: what does this do?
    status.value = 0
    hal_data["pwm"][pwmPortHandle.pin]["zero_latch"] = True


def setPWMPeriodScale(pwmPortHandle, squelchMask, status):
    status.value = 0
    hal_data["pwm"][pwmPortHandle.pin]["period_scale"] = squelchMask


def getPWMLoopTiming(status):
    status.value = 0
    return 0


def getPWMCycleStartTime(status):
    status.value = 0
    return 0


#############################################################################
# Ports.h
#############################################################################


def getNumAccumulators():
    return kNumAccumulators


def getNumAnalogTriggers():
    return kNumAnalogTriggers


def getNumAnalogInputs():
    return kNumAnalogInputs


def getNumAnalogOutputs():
    return kNumAnalogOutputs


def getNumCounters():
    return kNumCounters


def getNumDigitalHeaders():
    return kNumDigitalHeaders


def getNumPWMHeaders():
    return kNumPWMHeaders


def getNumDigitalChannels():
    return kNumDigitalChannels


def getNumPWMChannels():
    return kNumPWMChannels


def getNumDigitalPWMOutputs():
    return kNumDigitalPWMOutputs


def getNumEncoders():
    return kNumEncoders


def getNumInterrupts():
    return kNumInterrupts


def getNumRelayChannels():
    return kNumRelayChannels


def getNumRelayHeaders():
    return kNumRelayHeaders


def getNumPCMModules():
    return kNumPCMModules


def getNumSolenoidChannels():
    return kNumSolenoidChannels


def getNumPDPModules():
    return kNumPDPModules


def getNumPDPChannels():
    return kNumPDPChannels


#############################################################################
# Power
#############################################################################


def getVinVoltage(status):
    status.value = 0
    return hal_data["power"]["vin_voltage"]


def getVinCurrent(status):
    status.value = 0
    return hal_data["power"]["vin_current"]


def getUserVoltage6V(status):
    status.value = 0
    return hal_data["power"]["user_voltage_6v"]


def getUserCurrent6V(status):
    status.value = 0
    return hal_data["power"]["user_current_6v"]


def getUserActive6V(status):
    status.value = 0
    return hal_data["power"]["user_active_6v"]


def getUserCurrentFaults6V(status):
    status.value = 0
    return hal_data["power"]["user_faults_6v"]


def getUserVoltage5V(status):
    status.value = 0
    return hal_data["power"]["user_voltage_5v"]


def getUserCurrent5V(status):
    status.value = 0
    return hal_data["power"]["user_current_5v"]


def getUserActive5V(status):
    status.value = 0
    return hal_data["power"]["user_active_5v"]


def getUserCurrentFaults5V(status):
    status.value = 0
    return hal_data["power"]["user_faults_5v"]


def getUserVoltage3V3(status):
    status.value = 0
    return hal_data["power"]["user_voltage_3v3"]


def getUserCurrent3V3(status):
    status.value = 0
    return hal_data["power"]["user_current_3v3"]


def getUserActive3V3(status):
    status.value = 0
    return hal_data["power"]["user_active_3v3"]


def getUserCurrentFaults3V3(status):
    status.value = 0
    return hal_data["power"]["user_faults_3v3"]


#############################################################################
# Relay.h
#############################################################################


def _handle_to_channel(relayPortHandle):
    channel = int(relayPortHandle.pin / 2)
    return channel, relayPortHandle.pin % 2 == 0


def initializeRelayPort(portHandle, fwd, status):
    status.value = 0
    pin = portHandle.pin * 2
    if not fwd:
        pin = pin + 1
        hal_data["relay"][portHandle.pin]["rev"] = False
    else:
        hal_data["relay"][portHandle.pin]["fwd"] = False

    hal_data["relay"][portHandle.pin]["initialized"] = True

    return types.RelayHandle(pin)


def freeRelayPort(relayPortHandle):
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        hal_data["relay"][channel]["fwd"] = False
    else:
        hal_data["relay"][channel]["rev"] = False


def checkRelayChannel(channel):
    return 0 <= channel and channel < kNumRelayHeaders


def setRelay(relayPortHandle, on, status):
    status.value = 0
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        hal_data["relay"][channel]["fwd"] = on
    else:
        hal_data["relay"][channel]["rev"] = on


def getRelay(relayPortHandle, status):
    status.value = 0
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        return hal_data["relay"][channel]["fwd"]
    else:
        return hal_data["relay"][channel]["rev"]


#############################################################################
# SPI.h
#############################################################################

#
# SPI: These functions should never get called, pass a simPort object
#      to the SPI implementation instead. See spi_helpers.py for an
#      example.
#
#      The simPort object should implement all of the SPI functions below
#
# TODO: change WPILib HAL impl to take an object, then we can implement
#       the simport stuff at the HAL layer instead
#


def initializeSPI(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def transactionSPI(port, dataToSend, dataReceived, size):
    raise NotImplementedError("Not implemented in simulation")


def writeSPI(port, dataToSend, sendSize):
    raise NotImplementedError("Not implemented in simulation")


def readSPI(port, buffer, count):
    raise NotImplementedError("Not implemented in simulation")


def closeSPI(port):
    raise NotImplementedError("Not implemented in simulation")


def setSPISpeed(port, speed):
    raise NotImplementedError("Not implemented in simulation")


def setSPIOpts(port, msbFirst, sampleOnTrailing, clkIdleHigh):
    raise NotImplementedError("Not implemented in simulation")


def setSPIChipSelectActiveHigh(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSPIChipSelectActiveLow(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def getSPIHandle(port):
    raise NotImplementedError("Not implemented in simulation")


def setSPIHandle(port, handle):
    raise NotImplementedError("Not implemented in simulation")


def initSPIAuto(port, bufferSize, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def freeSPIAuto(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def startSPIAutoRate(port, period, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def startSPIAutoTrigger(
    port, digitalSourceHandle, analogTriggerType, triggerRising, triggerFalling, status
):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def stopSPIAuto(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSPIAutoTransmitData(port, dataToSend, dataSize, zeroSize, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def forceSPIAutoRead(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def readSPIAutoReceivedData(port, buffer, numToRead, timeout, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def getSPIAutoDroppedCount(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# SerialPort
#############################################################################

#
# Serial: These functions should never get called, pass a simPort object
#         to the SerialPort implementation instead. See serial_helpers.py
#         for an example.
#
#         The simPort object should implement all of thefunctions below
#


def initializeSerialPort(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def initializeSerialPortDirect(port, portName, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialBaudRate(port, baud, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialDataBits(port, bits, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialParity(port, parity, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialStopBits(port, stopBits, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialWriteMode(port, mode, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialFlowControl(port, flow, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialTimeout(port, timeout, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def enableSerialTermination(port, terminator, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def disableSerialTermination(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialReadBufferSize(port, size, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def setSerialWriteBufferSize(port, size, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def getSerialBytesReceived(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def readSerial(port, buffer, count, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def writeSerial(port, buffer, count, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def flushSerial(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def clearSerial(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


def closeSerial(port, status):
    status.value = 0
    raise NotImplementedError("Not implemented in simulation")


#############################################################################
# Solenoid
#############################################################################

# Note: if you're just using the default solenoid module, you can use
# hal_data['solenoid'][N] to refer to solenoids -- it's exactly the same
# data as hal_data['pcm'][0][N]


def initializeSolenoidPort(portHandle, status):
    if not checkSolenoidModule(portHandle.module):
        status.value = RESOURCE_OUT_OF_RANGE
        return

    if portHandle.module not in hal_data["pcm"]:
        hal_data["pcm"][portHandle.module] = [
            NotifyDict({"initialized": False, "value": None})
            for _ in range(kNumSolenoidChannels)
        ]

    data = _initport(portHandle.module, portHandle.pin, status, root=hal_data["pcm"])
    if data is None:
        return

    data["value"] = False
    return types.SolenoidHandle(portHandle)


def freeSolenoidPort(solenoidPortHandle):
    hal_data["pcm"][solenoidPortHandle.module][solenoidPortHandle.pin][
        "initialized"
    ] = False
    solenoidPortHandle.pin = None


def checkSolenoidModule(module):
    return module < kNumPCMModules and module >= 0


def checkSolenoidChannel(channel):
    return channel < kNumSolenoidChannels and channel >= 0


def getSolenoid(solenoidPortHandle, status):
    status.value = 0
    return hal_data["pcm"][solenoidPortHandle.module][solenoidPortHandle.pin]["value"]


def getAllSolenoids(module, status):
    status.value = 0
    value = 0
    if module in hal_data["pcm"]:
        for i, s in enumerate(hal_data["pcm"][module]):
            value |= (1 if s["value"] else 0) << i
    return value


def setSolenoid(solenoidPortHandle, value, status):
    status.value = 0
    hal_data["pcm"][solenoidPortHandle.module][solenoidPortHandle.pin]["value"] = value


def setAllSolenoids(module, state, status):
    status.value = 0
    if module not in hal_data["pcm"]:
        status.value = RESOURCE_OUT_OF_RANGE
    else:
        for i, s in enumerate(hal_data["pcm"][module]):
            s["value"] = True if state & (1 << i) else False


def getPCMSolenoidBlackList(module, status):
    status.value = 0
    return 0


def getPCMSolenoidVoltageStickyFault(module, status):
    status.value = 0
    return False


def getPCMSolenoidVoltageFault(module, status):
    status.value = 0
    return False


def clearAllPCMStickyFaults(module, status):
    status.value = 0


def setOneShotDuration(solenoidPortHandle, durMS, status):
    status.value = 0
    hal_data["pcm"][solenoidPortHandle.module][solenoidPortHandle.pin][
        "one_shot_duration"
    ] = durMS


def fireOneShot(solenoidPortHandle, status):
    status.value = 0
    # TODO: need to schedule a callback to implement this somehow
    raise NotImplementedError("Not implemented in simulation")


# This needs to be here otherwise tests will fail, as hal.initialize() does not call this
data._reset_hal_data(hooks)
