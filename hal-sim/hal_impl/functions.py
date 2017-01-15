
from hal import constants
from . import types

import operator

from . import data
from .data import hal_data
from hal_impl.sim_hooks import SimHooks

import logging
logger = logging.getLogger('hal')

hooks = SimHooks()

def reset_hal():
    data._reset_hal_data(hooks)
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
kNumAnalogOutputs = 2 # mxp only
kNumCounters = 8
kNumDigitalHeaders = 10
kNumDigitalMXPChannels = 16
kNumDigitalSPIPortChannels = 5
kNumPWMHeaders = 10
kNumDigitalChannels = kNumDigitalHeaders + kNumDigitalMXPChannels + kNumDigitalSPIPortChannels
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

#############################################################################
# HAL
#############################################################################

def sleep(s):
    hooks.delaySeconds(s)

def getPort(pin):
    return getPortWithModule(0, pin)

def getPortWithModule(module, pin):
    return types.PortHandle(pin, module)

def _getErrorMessage(code):
    if code == 0:
        return ''

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
        return  "HAL: A handle parameter was passed incorrectly"
    else:
        return "Unknown error status %s" % code
    
def getErrorMessage(code):
    return bytes(_getErrorMessage(code), 'utf-8')

def getFPGAVersion(status):
    status.value = 0
    return 2017

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
    return hal_data['fpga_button']

def getSystemActive(status):
    status.value = 0
    return True
    
def getBrownedOut(status):
    status.value = 0
    return False

def initialize(mode=0):
    #initializeNotifier()
    initializeDriverStation()
    
    return True

def report(resource, instanceNumber, context=0, feature=None):
    
    # TODO: Cover all interesting devices
    hur = constants.HALUsageReporting
    if resource ==  hur.kResourceType_Jaguar:
        hal_data['pwm'][instanceNumber]['type'] = 'jaguar'
    elif resource == hur.kResourceType_MindsensorsSD540:
        hal_data['pwm'][instanceNumber]['type'] = 'sd540'
    elif resource == hur.kResourceType_RevSPARK:
        hal_data['pwm'][instanceNumber]['type'] = 'spark'
    elif resource == hur.kResourceType_Talon:
        hal_data['pwm'][instanceNumber]['type'] = 'talon'
    elif resource == hur.kResourceType_TalonSRX:
        hal_data['pwm'][instanceNumber]['type'] = 'talonsrx'
    elif resource == hur.kResourceType_Victor:
        hal_data['pwm'][instanceNumber]['type'] = 'victor'
    elif resource == hur.kResourceType_VictorSP:
        hal_data['pwm'][instanceNumber]['type'] = 'victorsp'
    
    hal_data['reports'].setdefault(resource, []).append(instanceNumber)


#############################################################################
# Accelerometer.h
#############################################################################

def setAccelerometerActive(active):
    hal_data['accelerometer']['active'] = active

def setAccelerometerRange(range):
    hal_data['accelerometer']['range'] = range

def getAccelerometerX():
    return hal_data['accelerometer']['x']

def getAccelerometerY():
    return hal_data['accelerometer']['y']

def getAccelerometerZ():
    return hal_data['accelerometer']['z']

#############################################################################
# AnalogAccumulator.h
#############################################################################

def isAccumulatorChannel(analog_port, status):
    status.value = 0
    return analog_port.pin in kAccumulatorChannels

def initAccumulator(analog_port, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_initialized'] = True

def resetAccumulator(analog_port, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_center'] = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_count'] = 1
    hal_data['analog_in'][analog_port.pin]['accumulator_value'] = 0

def setAccumulatorCenter(analog_port, center, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_center'] = center

def setAccumulatorDeadband(analog_port, deadband, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_deadband'] = deadband

def getAccumulatorValue(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['accumulator_value']

def getAccumulatorCount(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['accumulator_count']

def getAccumulatorOutput(analog_port, status):
    status.value = 0
    return (hal_data['analog_in'][analog_port.pin]['accumulator_value'],
           hal_data['analog_in'][analog_port.pin]['accumulator_count'])

#############################################################################
# AnalogGyro.h
#############################################################################

def initializeAnalogGyro(handle, status):
    status.value = 0
    handle = types.GyroHandle(handle)
    
    try:
        data = hal_data['analog_gyro'][handle.pin]
    except IndexError:
        status.value = PARAMETER_OUT_OF_RANGE
        return
        
    if data['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return
    
    data['initialized'] = True
    
    data['offset'] = 0
    data['deadband'] = 0
    data['volts_per_degree'] = 0
    
    data['angle'] = 0
    data['rate'] = 0
    
    return handle

def setupAnalogGyro(handle, status):
    status.value = 0
    assert hal_data['analog_gyro'][handle.pin]['initialized']

def freeAnalogGyro(handle):
    hal_data['analog_gyro'][handle.pin]['initialized'] = False

def setAnalogGyroParameters(handle, voltsPerDegreePerSecond, offset, center, status):
    status.value = 0
    data = hal_data['analog_gyro'][handle.pin]
    data['volts_per_degree'] = voltsPerDegreePerSecond
    data['offset'] = offset
    data['center'] = center

def setAnalogGyroVoltsPerDegreePerSecond(handle, voltsPerDegreePerSecond, status):
    status.value = 0
    hal_data['analog_gyro'][handle.pin]['volts_per_degree'] = voltsPerDegreePerSecond

def resetAnalogGyro(handle, status):
    status.value = 0
    data = hal_data['analog_gyro'][handle.pin]
    data['rate'] = 0.0
    data['angle'] = 0.0

def calibrateAnalogGyro(handle, status):
    status.value = 0
    assert hal_data['analog_gyro'][handle.pin]['initialized']

def setAnalogGyroDeadband(handle, volts, status):
    status.value = 0
    hal_data['analog_gyro'][handle.pin]['deadband'] = volts 

def getAnalogGyroAngle(handle, status):
    status.value = 0
    return hal_data['analog_gyro'][handle.pin]['angle'] 

def getAnalogGyroRate(handle, status):
    status.value = 0
    return hal_data['analog_gyro'][handle.pin]['rate'] 

def getAnalogGyroOffset(handle, status):
    status.value = 0
    return hal_data['analog_gyro'][handle.pin]['offset'] 

def getAnalogGyroCenter(handle, status):
    status.value = 0
    return hal_data['analog_gyro'][handle.pin]['center'] 

#############################################################################
# AnalogInput.h
#############################################################################

def initializeAnalogInputPort(port, status):
    status.value = 0
    hal_data['analog_in'][port.pin]['initialized'] = True
    return types.AnalogInputHandle(port)

def freeAnalogInputPort(analog_port):
    hal_data['analog_in'][analog_port.pin]['initialized'] = False

def checkAnalogModule(module):
    return module == 1

def checkAnalogInputChannel(pin):
    return pin < kNumAnalogInputs and pin >= 0

def setAnalogSampleRate(samples_per_second, status):
    status.value = 0
    hal_data['analog_sample_rate'] = samples_per_second

def getAnalogSampleRate(status):
    status.value = 0
    return hal_data['analog_sample_rate']

def setAnalogAverageBits(analog_port, bits, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['avg_bits'] = bits

def getAnalogAverageBits(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['avg_bits']

def setAnalogOversampleBits(analog_port, bits, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['oversample_bits'] = bits

def getAnalogOversampleBits(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['oversample_bits']

def getAnalogValue(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['value']

def getAnalogAverageValue(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['avg_value']

def getAnalogVoltsToValue(analog_port, voltage, status):
    status.value = 0
    if voltage > 5.0:
        voltage = 5.0
        status.value = VOLTAGE_OUT_OF_RANGE
    elif voltage < 0.0:
        voltage = 0.0
        status.value = VOLTAGE_OUT_OF_RANGE

    LSBWeight = getAnalogLSBWeight(analog_port, status)
    offset = getAnalogOffset(analog_port, status)
    return (int)((voltage + offset * 1.0e-9) / (LSBWeight * 1.0e-9))

def getAnalogVoltage(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['voltage']

def getAnalogAverageVoltage(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['avg_voltage']

def getAnalogLSBWeight(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['lsb_weight']

def getAnalogOffset(analog_port, status):
    status.value = 0
    return hal_data['analog_in'][analog_port.pin]['offset']

#############################################################################
# AnalogOutput.h
#############################################################################

kTimebase = 40000000 #< 40 MHz clock
kDefaultOversampleBits = 0
kDefaultAverageBits = 7
kDefaultSampleRate = 50000.0

def initializeAnalogOutputPort(port, status):
    status.value = 0
    hal_data['analog_out'][port.pin]['initialized'] = True
    return types.AnalogOutputHandle(port)

def freeAnalogOutputPort(analog_port):
    hal_data['analog_out'][analog_port.pin]['initialized'] = False

def setAnalogOutput(analog_port, voltage, status):
    status.value = 0
    hal_data['analog_out'][analog_port.pin]['output'] = voltage

def getAnalogOutput(analog_port, status):
    status.value = 0
    return hal_data['analog_out'][analog_port.pin]['output']

def checkAnalogOutputChannel(pin):
    return pin < kNumAnalogOutputs and pin >= 0

#############################################################################
# AnalogTrigger.h
#############################################################################

def initializeAnalogTrigger(port, status):
    status.value = 0
    for idx in range(0, len(hal_data['analog_trigger'])):
        cnt = hal_data['analog_trigger'][idx]
        if cnt['initialized'] == False:
            cnt['initialized'] = True
            cnt['port'] = port
            return types.AnalogTriggerHandle(port, idx), idx

    status.value = NO_AVAILABLE_RESOURCES
    return None, -1

def cleanAnalogTrigger(analog_trigger, status):
    status.value = 0
    hal_data['analog_trigger'][analog_trigger.index]['initialized'] = False

def setAnalogTriggerLimitsRaw(analog_trigger, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR 
    else:
        status.value = 0
        hal_data['analog_trigger'][analog_trigger.index]['trig_lower'] = lower
        hal_data['analog_trigger'][analog_trigger.index]['trig_upper'] = upper

def setAnalogTriggerLimitsVoltage(analog_trigger, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR 
    else:
        status.value = 0
        analog_port = hal_data['analog_port'][analog_trigger.pin]
        hal_data['analog_trigger'][analog_trigger.index]['trig_lower'] = getAnalogVoltsToValue(analog_port, lower, status)
        hal_data['analog_trigger'][analog_trigger.index]['trig_upper'] = getAnalogVoltsToValue(analog_port, upper, status)
    

def setAnalogTriggerAveraged(analog_trigger, use_averaged_value, status):
    if hal_data['analog_trigger'][analog_trigger.index]['trig_type'] is 'filtered':
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0
        hal_data['analog_trigger'][analog_trigger.index]['trig_type'] = 'averaged' if use_averaged_value else None

def setAnalogTriggerFiltered(analog_trigger, use_filtered_value, status):
    if hal_data['analog_trigger'][analog_trigger.index]['trig_type'] is 'averaged':
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0    
        hal_data['analog_trigger'][analog_trigger.index]['trig_type'] = 'filtered' if use_filtered_value else None

def _get_trigger_value(analog_trigger):
    ain = hal_data['analog_in'][analog_trigger.pin]
    atr = hal_data['analog_trigger'][analog_trigger.index]
    trig_type = atr['trig_type']
    if trig_type is None:
        return atr, ain['value']
    if trig_type is 'averaged':
        return atr, ain['avg_value']
    if trig_type is 'filtered':
        return atr, ain['value'] # XXX
    assert False

def getAnalogTriggerInWindow(analog_trigger, status):
    status.value = 0
    atr, val = _get_trigger_value(analog_trigger)
    return val >= atr['trig_lower'] and val <= atr['trig_upper']
        
def getAnalogTriggerTriggerState(analog_trigger, status):
    # To work properly, this needs some other runtime component managing the
    # state variable too, but this works well enough
    status.value = 0
    atr, val = _get_trigger_value(analog_trigger)
    if val < atr['trig_lower']:
        atr['trig_state'] = False
        return False
    elif val > atr['trig_upper']:
        atr['trig_state'] = True
        return True
    else:
        return atr['trig_state']

def getAnalogTriggerOutput(analog_trigger, type, status):
    if type == constants.AnalogTriggerType.kInWindow:
        return getAnalogTriggerInWindow(analog_trigger, status)
    if type == constants.AnalogTriggerType.kState:
        return getAnalogTriggerTriggerState(analog_trigger, status)
    else:
        status.value = ANALOG_TRIGGER_PULSE_OUTPUT_ERROR
        return False


#############################################################################
# Compressor.h
#############################################################################

def initializeCompressor(module, status):
    status.value = 0
    assert module == 0 # don't support multiple modules for now
    hal_data['compressor']['initialized'] = True
    return types.CompressorHandle(module)

def checkCompressorModule(module):
    return module < 63

def getCompressor(compressorHandle, status):
    status.value = 0
    return hal_data['compressor']['on']

def setCompressorClosedLoopControl(compressorHandle, value, status):
    status.value = 0
    hal_data['compressor']['closed_loop_enabled'] = value

def getCompressorClosedLoopControl(compressorHandle, status):
    status.value = 0
    return hal_data['compressor']['closed_loop_enabled']

def getCompressorPressureSwitch(compressorHandle, status):
    status.value = 0
    return hal_data['compressor']['pressure_switch']

def getCompressorCurrent(compressorHandle, status):
    status.value = 0
    return hal_data['compressor']['current']

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
    for idx in range(0, len(hal_data['counter'])):
        cnt = hal_data['counter'][idx]
        if cnt['initialized'] == False:
            cnt['initialized'] = True
            cnt['mode'] = mode
            return types.CounterHandle(idx), idx 
    
    status.value = NO_AVAILABLE_RESOURCES
    return None, -1

def freeCounter(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['initialized'] = False

def setCounterAverageSize(counterHandle, size, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['average_size'] = size

def setCounterUpSource(counterHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    # AnalogInputs should be referred to by index, not pin
    try:
        hal_data['counter'][counterHandle.idx]['up_source_channel'] = digitalSourceHandle.index
    except AttributeError:
        hal_data['counter'][counterHandle.idx]['up_source_channel'] = digitalSourceHandle.pin
    hal_data['counter'][counterHandle.idx]['up_source_trigger'] = analogTriggerType
    
    if hal_data['counter'][counterHandle.idx]['mode'] in \
       [constants.CounterMode.kTwoPulse, constants.CounterMode.kExternalDirection]:
        setCounterUpSourceEdge(counterHandle, True, False, status) 

def setCounterUpSourceEdge(counterHandle, rising_edge, falling_edge, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['up_rising_edge'] = rising_edge
    hal_data['counter'][counterHandle.idx]['up_falling_edge'] = falling_edge

def clearCounterUpSource(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['up_rising_edge'] = False
    hal_data['counter'][counterHandle.idx]['up_falling_edge'] = False
    hal_data['counter'][counterHandle.idx]['up_source_channel'] = 0
    hal_data['counter'][counterHandle.idx]['up_source_trigger'] = False

def setCounterDownSource(counterHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    if hal_data['counter'][counterHandle.idx]['mode'] not in \
       [constants.CounterMode.kTwoPulse, constants.CounterMode.kExternalDirection]:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    # AnalogInputs should be referred to by index, not pin
    try:
        hal_data['counter'][counterHandle.idx]['down_source_channel'] = digitalSourceHandle.index
    except AttributeError:
        hal_data['counter'][counterHandle.idx]['down_source_channel'] = digitalSourceHandle.pin
    hal_data['counter'][counterHandle.idx]['down_source_trigger'] = analogTriggerType

def setCounterDownSourceEdge(counterHandle, rising_edge, falling_edge, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['down_rising_edge'] = rising_edge
    hal_data['counter'][counterHandle.idx]['down_falling_edge'] = falling_edge

def clearCounterDownSource(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['down_rising_edge'] = False
    hal_data['counter'][counterHandle.idx]['down_falling_edge'] = False
    hal_data['counter'][counterHandle.idx]['down_source_channel'] = 0
    hal_data['counter'][counterHandle.idx]['down_source_trigger'] = False

def setCounterUpDownMode(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['mode'] = constants.CounterMode.kTwoPulse

def setCounterExternalDirectionMode(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['mode'] = constants.CounterMode.kExternalDirection

def setCounterSemiPeriodMode(counterHandle, high_semi_period, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['mode'] = constants.CounterMode.kSemiperiod
    hal_data['counter'][counterHandle.idx]['up_rising_edge'] = high_semi_period
    hal_data['counter'][counterHandle.idx]['update_when_empty'] = False

def setCounterPulseLengthMode(counterHandle, threshold, status):
    hal_data['counter'][counterHandle.idx]['mode'] = constants.CounterMode.kPulseLength
    hal_data['counter'][counterHandle.idx]['pulse_length_threshold'] = threshold

def getCounterSamplesToAverage(counterHandle, status):
    status.value = 0
    return hal_data['counter'][counterHandle.idx]['samples_to_average']

def setCounterSamplesToAverage(counterHandle, samples_to_average, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['samples_to_average'] = samples_to_average

def resetCounter(counterHandle, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['count'] = 0

def getCounter(counterHandle, status):
    status.value = 0
    return hal_data['counter'][counterHandle.idx]['count']

def getCounterPeriod(counterHandle, status):
    status.value = 0
    return hal_data['counter'][counterHandle.idx]['period']

def setCounterMaxPeriod(counterHandle, max_period, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['max_period'] = max_period

def setCounterUpdateWhenEmpty(counterHandle, enabled, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['update_when_empty'] = enabled

def getCounterStopped(counterHandle, status):
    status.value = 0
    cnt = hal_data['counter'][counterHandle.idx]
    return cnt['period'] > cnt['max_period']

def getCounterDirection(counterHandle, status):
    status.value = 0
    return hal_data['counter'][counterHandle.idx]['direction']

def setCounterReverseDirection(counterHandle, reverse_direction, status):
    status.value = 0
    hal_data['counter'][counterHandle.idx]['reverse_direction'] = reverse_direction



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

# def allocateDIO(digital_port, input, status):
#     status.value = 0
#     if digital_port.pin >= kNumDigitalHeaders:
#         mxp_port = _remapMXPChannel(digital_port.pin)
#         if hal_data["mxp"][mxp_port]["initialized"]:
#             status.value = RESOURCE_IS_ALLOCATED
#             return False
#     dio = hal_data['dio'][digital_port.pin]
#     if dio['initialized']:
#         status.value = RESOURCE_IS_ALLOCATED
#         return False
#     if digital_port.pin >= kNumDigitalHeaders:
#         hal_data["mxp"][mxp_port]["initialized"] = True
#     dio['initialized'] = True
#     dio['is_input'] = input


# def freeDIO(digital_port, status):
#     status.value = 0
#     hal_data['dio'][digital_port.pin]['initialized'] = False
#     if digital_port.pin >= kNumDigitalHeaders:
#         mxp_port = _remapMXPChannel(digital_port.pin)
#         hal_data["mxp"][mxp_port]["initialized"] = False



def initializeDIOPort(portHandle, input, status):
    status.value = 0
    if portHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPChannel(portHandle.pin)
        if hal_data["mxp"][mxp_port]["initialized"]:
            status.value = RESOURCE_IS_ALLOCATED
            return False
    dio = hal_data['dio'][portHandle.pin]
    if dio['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return False
    if portHandle.pin >= kNumDigitalHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True
    dio['initialized'] = True
    dio['is_input'] = input
    return types.DigitalHandle(portHandle)

def checkDIOChannel(channel):
    return channel < kNumDigitalChannels and channel >= 0

def freeDIOPort(dioPortHandle):
    hal_data['dio'][dioPortHandle.pin]['initialized'] = False
    if dioPortHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPChannel(dioPortHandle.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False
    dioPortHandle.pin = None

def allocateDigitalPWM(status):
    status.value = 0
    return types.DigitalPWMHandle()

def freeDigitalPWM(pwmGenerator, status):
    status.value = 0
    hal_data['d0_pwm'][pwmGenerator.pin]['pin'] = None

def setDigitalPWMRate(rate, status):
    status.value = 0
    hal_data['d0_pwm_rate'] = rate

def setDigitalPWMDutyCycle(pwmGenerator, dutyCycle, status):
    status.value = 0
    hal_data['d0_pwm'][pwmGenerator.pin]['duty_cycle'] = dutyCycle

def setDigitalPWMOutputChannel(pwmGenerator, channel, status):
    status.value = 0
    hal_data['d0_pwm'][pwmGenerator.pin]['pin'] = channel

def setDIO(dioPortHandle, value, status):
    status.value = 0
    hal_data['dio'][dioPortHandle.pin]['value'] = True if value else False

def getDIO(dioPortHandle, status):
    status.value = 0
    return bool(hal_data['dio'][dioPortHandle.pin]['value'])

def getDIODirection(dioPortHandle, status):
    status.value = 0
    return hal_data['dio'][dioPortHandle.pin]['is_input']

def pulse(dioPortHandle, pulse_length, status):
    status.value = 0
    hal_data['dio'][dioPortHandle.pin]['pulse_length'] = pulse_length

def isPulsing(dioPortHandle, status):
    status.value = 0
    return hal_data['dio'][dioPortHandle.pin]['pulse_length'] is not None

def isAnyPulsing(status):
    status.value = 0
    
    for p in hal_data['dio']:
        if p is not None and p['pulse_length'] is not None:
            return True
    return False
    
def setFilterSelect(dioPortHandle, filterIndex, status):
    if filterIndex < 0 or filterIndex > 3:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    
    if filterIndex == 0:
        filterIndex = hal_data['dio'][dioPortHandle.pin]['filterIndex']
        hal_data['dio'][dioPortHandle.pin]['filterIndex'] = None
        hal_data['filter'][filterIndex]['enabled'] = False
    else:
        filterIndex = filterIndex - 1
        hal_data['filter'][filterIndex]['enabled'] = True
        hal_data['dio'][dioPortHandle.pin]['filterIndex'] = filterIndex
    status.value = 0

def getFilterSelect(dioPortHandle, status):
    status.value = 0
    filterIndex = hal_data['dio'][dioPortHandle.pin]['filterIndex']
    if filterIndex is None:
        return 0
    else:
        return filterIndex + 1 # really?

def setFilterPeriod(filterIndex, value, status):
    if filterIndex < 0 or filterIndex > 2:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    
    status.value = 0
    hal_data['filter'][filterIndex]['period'] = value

def getFilterPeriod(filterIndex, status):
    if filterIndex < 0 or filterIndex > 2:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    
    status.value = 0
    return hal_data['filter'][filterIndex]['period']


#############################################################################
# DriverStation.h
#############################################################################

def setErrorData(errors, errorsLength, waitMs):
    # Nothing calls this anymore
    pass

def sendError(isError, errorCode, isLVCode, details, location, callStack, printMsg):
    # the only thing that calls this is DriverStation.ReportError
    # and it logs by default now
    hal_data['error_data'] = (isError, details, location)

def getControlWord(controlWord):
    controlWord.__dict__.update(hal_data['control'])

def getAllianceStation(status):
    status.value = 0
    return hal_data['alliance_station']

def getJoystickAxes(joystickNum, axes):
    axes.axes = list(map(float, hal_data['joysticks'][joystickNum]['axes']))
    axes.count = len(axes.axes)

def getJoystickPOVs(joystickNum, povs):
    povs.povs = list(map(int, hal_data['joysticks'][joystickNum]['povs']))
    povs.count = len(povs.povs)

def getJoystickButtons(joystickNum, buttons):
    # buttons are stored as booleans for ease of use, convert to integer
    b = hal_data['joysticks'][joystickNum]['buttons']
    # profiled optimization
    #buttons.buttons = sum(int(v) << i for i, v in enumerate(b[1:]))
    l = len(b)-1
    buttons.buttons = sum(map(operator.lshift, map(int, b[1:]), range(l)))
    buttons.count = l

def getJoystickDescriptor(joystickNum, desc):
    stick = hal_data["joysticks"][joystickNum]
    desc.isXbox = stick["isXbox"]
    desc.type = stick["type"]
    desc.name = stick["name"]
    desc.axisCount = stick["axisCount"]
    desc.buttonCount = stick["buttonCount"]

def getJoystickIsXbox(joystickNum):
    return hal_data["joysticks"][joystickNum]["isXbox"]

def getJoystickType(joystickNum):
    return hal_data["joysticks"][joystickNum]["type"]

def getJoystickName(joystickNum):
    return hal_data["joysticks"][joystickNum]["name"]

def getJoystickAxisType(joystickNum, axis):
    assert False

def setJoystickOutputs(joystickNum, outputs, leftRumble, rightRumble):
    hal_data['joysticks'][joystickNum]["leftRumble"] = leftRumble
    hal_data['joysticks'][joystickNum]["rightRumble"] = rightRumble
    hal_data['joysticks'][joystickNum]["outputs"] = [bool(val) for val in bin(outputs)]

def getMatchTime(status):
    '''
        Returns approximate match time:
        - At beginning of autonomous, time is 0
        - At beginning of teleop, time is set to 15
        - If robot is disabled, time is 0
    '''
    status.value = 0
    match_start = hal_data['time']['match_start']
    if match_start is None:
        return 0.0
    else:
        return (hooks.getFPGATime() - hal_data['time']['match_start'])/1000000.0

def waitForDSData():
    with hooks.ds_cond:
        hooks.ds_cond.wait()

def initializeDriverStation():
    hooks.initializeDriverStation()

def observeUserProgramStarting():
    hal_data['user_program_state'] = 'starting'

def observeUserProgramDisabled():
    hal_data['user_program_state'] = 'disabled'

def observeUserProgramAutonomous():
    hal_data['user_program_state'] = 'autonomous'

def observeUserProgramTeleop():
    hal_data['user_program_state'] = 'teleop'

def observeUserProgramTest():
    hal_data['user_program_state'] = 'test'


#############################################################################
# Encoder.h
#############################################################################

def initializeEncoder(digitalSourceHandleA, analogTriggerTypeA, digitalSourceHandleB, analogTriggerTypeB, reverseDirection, encodingType, status):
    status.value = 0
    for idx in range(0, len(hal_data['encoder'])):
        enc = hal_data['encoder'][idx]
        if enc['initialized'] == False:
            enc['initialized'] = True

            enc['config'] = {"ASource_Channel": digitalSourceHandleA.pin, "ASource_AnalogTrigger": analogTriggerTypeA,
                             "BSource_Channel": digitalSourceHandleB.pin, "BSource_AnalogTrigger": analogTriggerTypeB}
            enc['reverse_direction'] = reverseDirection
            return types.EncoderHandle(idx), idx
    status.value = NO_AVAILABLE_RESOURCES
    return None, -1

def freeEncoder(encoder, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['initialized'] = False

def getEncoder(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['count']

def getEncoderRaw(encoderHandle, status):
    status.value = 0
    assert False

def getEncoderEncodingScale(encoderHandle, status):
    status.value = 0
    assert False

def resetEncoder(encoder, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['count'] = 0

def getEncoderPeriod(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['period']

def setEncoderMaxPeriod(encoder, max_period, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['max_period'] = max_period

def getEncoderStopped(encoder, status):
    status.value = 0
    enc = hal_data['encoder'][encoder.idx]
    return enc['period'] > enc['max_period']

def getEncoderDirection(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['direction']

def getEncoderDistance(encoderHandle, status):
    status.value = 0
    enc = hal_data['encoder'][encoderHandle.idx]
    return enc['count']*enc['distance_per_pulse']

def getEncoderRate(encoderHandle, status):
    status.value = 0
    return hal_data['encoder'][encoderHandle.idx]['rate']

def setEncoderMinRate(encoderHandle, minRate, status):
    status.value = 0
    hal_data['encoder'][encoderHandle.idx]['min_rate'] = minRate

def setEncoderDistancePerPulse(encoderHandle, distancePerPulse, status):
    status.value = 0
    hal_data['encoder'][encoderHandle.idx]['distance_per_pulse'] = distancePerPulse

def setEncoderReverseDirection(encoder, reverse_direction, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['reverse_direction'] = reverse_direction

def setEncoderSamplesToAverage(encoder, samples_to_average, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['samples_to_average'] = samples_to_average

def getEncoderSamplesToAverage(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['samples_to_average']

def setEncoderIndexSource(encoderHandle, digitalSourceHandle, analogTriggerType, type, status):
    status.value = 0
    index_conf = {"IndexSource_Channel": digitalSourceHandle.pin, "IndexSource_AnalogTrigger": analogTriggerType,
                  "IndexType": type}
    hal_data['encoder'][encoderHandle.idx]['config'].update(index_conf)

def getEncoderFPGAIndex(encoderHandle, status):
    status.value = 0
    assert False

def getEncoderDecodingScaleFactor(encoderHandle, status):
    status.value = 0
    assert False

def getEncoderDistancePerPulse(encoderHandle, status):
    status.value = 0
    return hal_data['encoder'][encoderHandle.idx]['distance_per_pulse']

def getEncoderEncodingType(encoderHandle, status):
    status.value = 0
    assert False


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
    assert False

def transactionI2C(port, deviceAddress, dataToSend, sendSize, dataReceived, receiveSize):
    assert False

def writeI2C(port, deviceAddress, dataToSend, sendSize):
    assert False

def readI2C(port, deviceAddress, buffer, count):
    assert False

def closeI2C(port):
    assert False

#############################################################################
# Interrupts
#############################################################################

def initializeInterrupts(watcher, status):
    assert False # TODO

def cleanInterrupts(interrupt, status):
    assert False # TODO

def waitForInterrupt(interrupt, timeout, ignorePrevious, status):
    assert False # TODO

def enableInterrupts(interrupt, status):
    assert False # TODO

def disableInterrupts(interrupt, status):
    assert False # TODO

def readInterruptRisingTimestamp(interrupt, status):
    assert False # TODO

def readInterruptFallingTimestamp(interrupt, status):
    assert False # TODO

def requestInterrupts(interruptHandle, digitalSourceHandle, analogTriggerType, status):
    status.value = 0
    assert False

def attachInterruptHandler(interrupt, handler, param, status):
    assert False # TODO

def attachInterruptHandlerThreaded(interruptHandle, handler, param, status):
    status.value = 0
    assert False

def setInterruptUpSourceEdge(interrupt, rising_edge, falling_edge, status):
    assert False # TODO


#############################################################################
# Notifier
#############################################################################

# def initializeNotifier(processQueue, param, status):
#     assert False # TODO
# 
# def cleanNotifier(notifier, status):
#     assert False # TODO
#     
# def getNotifierParam(notifier, status):
#     assert False # TODO
# 
# def updateNotifierAlarm(notifier, triggerTime, status):
#     assert False # TODO
# 
# def stopNotifierAlarm(notifier, status):
#     assert False # TODO

#############################################################################
# PDP
#############################################################################

def initializePDP(module, status):
    status.value = 0
    
def checkPDPChannel(channel):
    return channel < kNumPDPChannels and channel >= 0

def checkPDPModule(module):
    return module < kNumPDPModules and module >= 0

def getPDPTemperature(module, status):
    status.value = 0
    return hal_data['pdp']['temperature']

def getPDPVoltage(module, status):
    status.value = 0
    return hal_data['pdp']['voltage']

def getPDPChannelCurrent(module, channel, status):
    if channel < 0 or channel >= len(hal_data['pdp']['current']):
        status.value = CTR_InvalidParamValue
        return 0
    status.value = 0
    return hal_data['pdp']['current'][channel]

def getPDPTotalCurrent(module, status):
    status.value = 0
    return hal_data['pdp']['total_current']

def getPDPTotalPower(module, status):
    status.value = 0
    return hal_data['pdp']['total_power']

def getPDPTotalEnergy(module, status):
    status.value = 0
    return hal_data['pdp']['total_energy']

def resetPDPTotalEnergy(module, status):
    status.value = 0
    hal_data['pdp']['total_energy'] = 0

def clearPDPStickyFaults(module, status):
    status.value = 0
    # not sure what to do here?

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
 
    if hal_data['pwm'][pwmPortHandle.pin]['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return
     
    hal_data['pwm'][pwmPortHandle.pin]['initialized'] = True
 
    if pwmPortHandle.pin >= kNumDigitalHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True
 
    return pwmPortHandle

def freePWMPort(pwmPortHandle, status):
    status.value = 0
    
    assert hal_data['pwm'][pwmPortHandle.pin]['initialized']
    hal_data['pwm'][pwmPortHandle.pin]['initialized'] = False
    hal_data['pwm'][pwmPortHandle.pin]['raw_value'] = 0
    hal_data['pwm'][pwmPortHandle.pin]['value'] = 0
    hal_data['pwm'][pwmPortHandle.pin]['period_scale'] = None
    hal_data['pwm'][pwmPortHandle.pin]['zero_latch'] = False
    hal_data['pwm'][pwmPortHandle.pin]['elim_deadband'] = False
 
    if pwmPortHandle.pin >= kNumDigitalHeaders:
        mxp_port = _remapMXPPWMChannel(pwmPortHandle.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False
        
    pwmPortHandle.pin = None

def checkPWMChannel(channel):
    return channel < kNumPWMChannels and channel >= 0

def setPWMConfig(pwmPortHandle, maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status):
    status.value = 0
    # ignored

def setPWMConfigRaw(pwmPortHandle, maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status):
    status.value = 0
    # ignored

def getPWMConfigRaw(pwmPortHandle, status): #, maxPwm, deadbandMaxPwm, centerPwm, deadbandMinPwm, minPwm, status):
    status.value = 0
    raise NotImplementedError

def setPWMEliminateDeadband(pwmPortHandle, eliminateDeadband, status):
    status.value = 0
    hal_data['pwm'][pwmPortHandle.pin]['elim_deadband'] = eliminateDeadband

def getPWMEliminateDeadband(pwmPortHandle, status):
    status.value = 0
    return hal_data['pwm'][pwmPortHandle.pin]['elim_deadband']

def setPWMRaw(pwmPortHandle, value, status):
    status.value = 0
    hal_data['pwm'][pwmPortHandle.pin]['raw_value'] = value

def setPWMSpeed(pwmPortHandle, speed, status):
    status.value = 0
    speed = min(max(speed, -1.0), 1.0)
    hal_data['pwm'][pwmPortHandle.pin]['value'] = speed

def setPWMPosition(pwmPortHandle, position, status):
    status.value = 0
    position = min(max(position, 0), 1.0)
    hal_data['pwm'][pwmPortHandle.pin]['value'] = position

def setPWMDisabled(pwmPortHandle, status):
    setPWMRaw(pwmPortHandle, 0, status)
    setPWMSpeed(pwmPortHandle, 0, status)
    setPWMPosition(pwmPortHandle, 0, status)

def getPWMRaw(pwmPortHandle, status):
    status.value = 0
    return hal_data['pwm'][pwmPortHandle.pin]['raw_value']

def getPWMSpeed(pwmPortHandle, status):
    status.value = 0
    return hal_data['pwm'][pwmPortHandle.pin]['value']

def getPWMPosition(pwmPortHandle, status):
    status.value = 0
    return hal_data['pwm'][pwmPortHandle.pin]['value']

def latchPWMZero(pwmPortHandle, status):
    # TODO: what does this do?
    status.value = 0
    hal_data['pwm'][pwmPortHandle.pin]['zero_latch'] = True

def setPWMPeriodScale(pwmPortHandle, squelchMask, status):
    status.value = 0
    hal_data['pwm'][pwmPortHandle.pin]['period_scale'] = squelchMask

def getLoopTiming(status):
    status.value = 0
    return hal_data['pwm_loop_timing']


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
    return hal_data['power']['vin_voltage']

def getVinCurrent(status):
    status.value = 0
    return hal_data['power']['vin_current']

def getUserVoltage6V(status):
    status.value = 0
    return hal_data['power']['user_voltage_6v']

def getUserCurrent6V(status):
    status.value = 0
    return hal_data['power']['user_current_6v']

def getUserActive6V(status):
    status.value = 0
    return hal_data['power']['user_active_6v']

def getUserCurrentFaults6V(status):
    status.value = 0
    return hal_data['power']['user_faults_6v']

def getUserVoltage5V(status):
    status.value = 0
    return hal_data['power']['user_voltage_5v']

def getUserCurrent5V(status):
    status.value = 0
    return hal_data['power']['user_current_5v']

def getUserActive5V(status):
    status.value = 0
    return hal_data['power']['user_active_5v']

def getUserCurrentFaults5V(status):
    status.value = 0
    return hal_data['power']['user_faults_5v']

def getUserVoltage3V3(status):
    status.value = 0
    return hal_data['power']['user_voltage_3v3']

def getUserCurrent3V3(status):
    status.value = 0
    return hal_data['power']['user_current_3v3']

def getUserActive3V3(status):
    status.value = 0
    return hal_data['power']['user_active_3v3']

def getUserCurrentFaults3V3(status):
    status.value = 0
    return hal_data['power']['user_faults_3v3']

#############################################################################
# Relay.h
#############################################################################

def _handle_to_channel(relayPortHandle):
    channel = int(relayPortHandle.pin/2)
    return channel, relayPortHandle.pin % 2 == 0

def initializeRelayPort(portHandle, fwd, status):
    status.value = 0
    pin = portHandle.pin * 2
    if not fwd:
        pin = pin + 1
        hal_data['relay'][portHandle.pin]['rev'] = False
    else:
        hal_data['relay'][portHandle.pin]['fwd'] = False

    hal_data['relay'][portHandle.pin]['initialized'] = True

    return types.RelayHandle(pin)

def freeRelayPort(relayPortHandle):
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        hal_data['relay'][channel]['fwd'] = False
    else:
        hal_data['relay'][channel]['rev'] = False

    
def checkRelayChannel(channel):
    return 0 <= channel and channel < kNumRelayHeaders

def setRelay(relayPortHandle, on, status):
    status.value = 0
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        hal_data['relay'][channel]['fwd'] = on
    else:
        hal_data['relay'][channel]['rev'] = on

def getRelay(relayPortHandle, status):
    status.value = 0
    if not relayPortHandle:
        return False
    channel, fwd = _handle_to_channel(relayPortHandle)
    if fwd:
        return hal_data['relay'][channel]['fwd']
    else:
        return hal_data['relay'][channel]['rev']

# def setRelayForward(digital_port, on, status):
#     status.value = 0
#     relay = hal_data['relay'][digital_port.pin]
#     relay['initialized'] = True
#     relay['fwd'] = on
# 
# def setRelayReverse(digital_port, on, status):
#     status.value = 0
#     relay = hal_data['relay'][digital_port.pin]
#     relay['initialized'] = True
#     relay['rev'] = on
# 
# def getRelayForward(digital_port, status):
#     return hal_data['relay'][digital_port.pin]['fwd']
# 
# def getRelayReverse(digital_port, status):
#     status.value = 0
#     return hal_data['relay'][digital_port.pin]['rev']


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
    assert False

def transactionSPI(port, dataToSend, dataReceived, size):
    assert False

def writeSPI(port, dataToSend, sendSize):
    assert False

def readSPI(port, buffer, count):
    assert False

def closeSPI(port):
    assert False

def setSPISpeed(port, speed):
    assert False

def setSPIOpts(port, msbFirst, sampleOnTrailing, clkIdleHigh):
    assert False

def setSPIChipSelectActiveHigh(port, status):
    status.value = 0
    assert False

def setSPIChipSelectActiveLow(port, status):
    status.value = 0
    assert False

def getSPIHandle(port):
    assert False

def setSPIHandle(port, handle):
    assert False

def initSPIAccumulator(port, period, cmd, xferSize, validMask, validValue, dataShift, dataSize, isSigned, bigEndian, status):
    status.value = 0
    assert False

def freeSPIAccumulator(port, status):
    status.value = 0
    assert False

def resetSPIAccumulator(port, status):
    status.value = 0
    assert False

def setSPIAccumulatorCenter(port, center, status):
    status.value = 0
    assert False

def setSPIAccumulatorDeadband(port, deadband, status):
    status.value = 0
    assert False

def getSPIAccumulatorLastValue(port, status):
    status.value = 0
    assert False

def getSPIAccumulatorValue(port, status):
    status.value = 0
    assert False

def getSPIAccumulatorCount(port, status):
    status.value = 0
    assert False

def getSPIAccumulatorAverage(port, status):
    status.value = 0
    assert False

def getSPIAccumulatorOutput(port, status):
    status.value = 0
    assert False


#############################################################################
# Solenoid
#############################################################################

def initializeSolenoidPort(port, status):
    
    if not checkSolenoidChannel(port.pin):
        status.value = RESOURCE_OUT_OF_RANGE
        return
    
    if hal_data['solenoid'][port.pin]['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return
    
    status.value = 0
    hal_data['solenoid'][port.pin]['initialized'] = True
    hal_data['solenoid'][port.pin]['value'] = False
    return types.SolenoidHandle(port)

def freeSolenoidPort(port):
    hal_data['solenoid'][port.pin]['initialized'] = False
    port.pin = None

def checkSolenoidModule(module):
    return module < kNumPCMModules and module >= 0

def checkSolenoidChannel(channel):
    return channel < kNumSolenoidChannels and channel >= 0

def getSolenoid(solenoid_port, status):
    status.value = 0
    return hal_data['solenoid'][solenoid_port.pin]['value']

def getAllSolenoids(module, status):
    status.value = 0
    value = 0
    for i, s in enumerate(hal_data['solenoid']):
        value |= (1 if s['value'] else 0) << i
    return value

def setSolenoid(solenoid_port, value, status):
    status.value = 0
    hal_data['solenoid'][solenoid_port.pin]['value'] = value

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
    return False


reset_hal()
