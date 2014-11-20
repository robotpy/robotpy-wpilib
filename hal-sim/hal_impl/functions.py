
from hal import constants
from . import types

import time
import threading

from .data import hal_data

#
# Misc constants
#

CTR_RxTimeout = 1
CTR_TxTimeout = 2
CTR_InvalidParamValue = 3
CTR_UnexpectedArbId = 4

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

#############################################################################
# Semaphore
#############################################################################

# constants
SEMAPHORE_Q_FIFO = 0x01
SEMAPHORE_Q_PRIORITY = 0x01
SEMAPHORE_DELETE_SAFE = 0x04
SEMAPHORE_INVERSION_SAFE = 0x08
SEMAPHORE_NO_WAIT = 0
SEMAPHORE_WAIT_FOREVER = -1
SEMAPHORE_EMPTY = 0
SEMAPHORE_FULL = 1

def initializeMutexRecursive():
    return types.MUTEX_ID(threading.RLock())

def initializeMutexNormal():
    return types.MUTEX_ID(threading.Lock())

def deleteMutex(sem):
    sem.lock = None

def takeMutex(sem):
    sem.lock.acquire()
    return 0

def tryTakeMutex(sem):
    if not sem.lock.acquire(False):
        return -1
    return 0

def giveMutex(sem):
    sem.lock.release()
    return 0

def initializeSemaphore(initial_value):
    return types.SEMAPHORE_ID(threading.Semaphore(initial_value))

def deleteSemaphore(sem):
    sem.sem = None

def takeSemaphore(sem):
    sem.sem.acquire()

def tryTakeSemaphore(sem):
    if not sem.sem.acquire(False):
        return -1
    return 0

def giveSemaphore(sem):
    sem.sem.release()

def initializeMultiWait():
    return types.MULTIWAIT_ID(threading.Condition())

def deleteMultiWait(sem):
    sem.cond = None

def takeMultiWait(sem, mutex, timeout):
    sem.cond.wait() # timeout is ignored in C++ HAL

def giveMultiWait(sem):
    sem.cond.notifyAll() # hal uses pthread_cond_broadcast, which wakes all threads


#############################################################################
# HAL
#############################################################################

def getPort(pin):
    return getPortWithModule(0, pin)

def getPortWithModule(module, pin):
    return types.Port(pin, module)

def getHALErrorMessage(code):
    if code == 0:
        return ''

    elif code == CTR_RxTimeout:
        return "CTRE CAN Recieve Timeout"
    elif code == CTR_InvalidParamValue:
        return "CTRE CAN Invalid Parameter"
    elif code == CTR_UnexpectedArbId:
        return "CTRE Unexpected Arbitration ID (CAN Node ID)"
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

    else:
        return "Unknown error status"

def getFPGAVersion(status):
    status.value = 0
    return 2015

def getFPGARevision(status):
    status.value = 0
    return 0

def getFPGATime(status):
    status.value = 0
    return int((time.monotonic() - hal_data['program_start']) * 100000)

def getFPGAButton(status):
    status.value = 0
    return hal_data['fpga_button']

def HALSetErrorData(errors, errorsLength, wait_ms):
    hal_data['error_data'] = errors

def HALGetControlWord():
    return types.HALControlWord(hal_data['control'])

def HALGetAllianceStation():
    return hal_data['alliance_station']

def HALGetJoystickAxes(joystickNum, axes):
    # we store as -1 to 1 for ease of use, so convert to -128 to 127 here
    return [int(a*128) if a < 0 else int(a*127) for a in hal_data['joysticks'][joystickNum]['axes']]

def HALGetJoystickPOVs(joystickNum, povs):
    return map(int, hal_data['joysticks'][joystickNum]['povs'][:])

def HALGetJoystickButtons(joystickNum, buttons, count):
    # buttons are stored as booleans for ease of use, convert to integer
    b = hal_data['joysticks'][joystickNum]['buttons']
    buttons.value = sum(int(v) << i for i, v in enumerate(b[1:]))
    buttons.count = len(b)-1

def HALGetSystemActive(status):
    status.value = 0
    return True

def HALGetBrownedOut(status):
    status.value = 0
    return False

def HALSetNewDataSem(sem):
    pass

def HALInitialize(mode=0):
    return True

def HALNetworkCommunicationObserveUserProgramStarting():
    hal_data['user_program_state'] = 'starting'

def HALNetworkCommunicationObserveUserProgramDisabled():
    hal_data['user_program_state'] = 'disabled'

def HALNetworkCommunicationObserveUserProgramAutonomous():
    hal_data['user_program_state'] = 'autonomous'

def HALNetworkCommunicationObserveUserProgramTeleop():
    hal_data['user_program_state'] = 'teleop'

def HALNetworkCommunicationObserveUserProgramTest():
    hal_data['user_program_state'] = 'test'

def HALReport(resource, instanceNumber, context=0, feature=None):
    # TODO: context/feature?
    hal_data['reports'].setdefault(resource, []).append(instanceNumber)


#############################################################################
# Accelerometer
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
# Analog
#############################################################################

kTimebase = 40000000 #< 40 MHz clock
kDefaultOversampleBits = 0
kDefaultAverageBits = 7
kDefaultSampleRate = 50000.0
kAnalogInputPins = 8
kAnalogOutputPins = 2

kAccumulatorNumChannels = 2
kAccumulatorChannels = [0, 1]

def _checkAnalogIsFree(port):
    if port.pin < kAnalogOutputPins:
        assert hal_data['analog_out'][port.pin]['initialized'] == False
    assert hal_data['analog_in'][port.pin]['initialized'] == False

def initializeAnalogOutputPort(port, status):
    _checkAnalogIsFree(port)
    status.value = 0
    hal_data['analog_out'][port.pin]['initialized'] = True
    return types.AnalogPort(port)

def setAnalogOutput(analog_port, voltage, status):
    status.value = 0
    hal_data['analog_out'][analog_port.pin]['output'] = voltage

def getAnalogOutput(analog_port, status):
    status.value = 0
    return hal_data['analog_out'][analog_port.pin]['output']

def checkAnalogOutputChannel(pin):
    return pin < kAnalogOutputPins

def initializeAnalogInputPort(port, status):
    _checkAnalogIsFree(port)
    status.value = 0
    hal_data['analog_in'][port.pin]['initialized'] = True
    return types.AnalogPort(port)

def checkAnalogModule(module):
    return module == 1

def checkAnalogInputChannel(pin):
    return pin < kAnalogInputPins

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

def isAccumulatorChannel(analog_port, status):
    status.value = 0
    return analog_port.pin in kAccumulatorChannels

def initAccumulator(analog_port, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_initialized'] = True

def resetAccumulator(analog_port, status):
    status.value = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_center'] = 0
    hal_data['analog_in'][analog_port.pin]['accumulator_count'] = 0
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

def initializeAnalogTrigger(port, status):
    _checkAnalogIsFree(port)
    status.value = 0
    return types.AnalogTrigger(port)

def cleanAnalogTrigger(analog_trigger, status):
    status.value = 0
    hal_data['analog_in'][analog_trigger.pin]['initialized'] = False

def setAnalogTriggerLimitsRaw(analog_trigger, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR 
    else:
        status.value = 0
        hal_data['analog_in'][analog_trigger.pin]['trig_lower'] = lower
        hal_data['analog_in'][analog_trigger.pin]['trig_upper'] = upper

def setAnalogTriggerLimitsVoltage(analog_trigger, lower, upper, status):
    if lower > upper:
        status.value = ANALOG_TRIGGER_LIMIT_ORDER_ERROR 
    else:
        status.value = 0 
        hal_data['analog_in'][analog_trigger.pin]['trig_lower'] = getAnalogVoltsToValue(analog_trigger, lower, status)
        hal_data['analog_in'][analog_trigger.pin]['trig_upper'] = getAnalogVoltsToValue(analog_trigger, upper, status)
    

def setAnalogTriggerAveraged(analog_trigger, use_averaged_value, status):
    if hal_data['analog_in'][analog_trigger.pin]['trig_type'] is 'filtered':
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0    
        hal_data['analog_in'][analog_trigger.pin]['trig_type'] = 'averaged' if use_averaged_value else None

def setAnalogTriggerFiltered(analog_trigger, use_filtered_value, status):
    if hal_data['analog_in'][analog_trigger.pin]['trig_type'] is 'averaged':
        status.value = INCOMPATIBLE_STATE
    else:
        status.value = 0    
        hal_data['analog_in'][analog_trigger.pin]['trig_type'] = 'filtered' if use_filtered_value else None

def _get_trigger_value(analog_trigger):
    ain = hal_data['analog_in'][analog_trigger.pin]
    trig_type = ain['trig_type']
    if trig_type is None:
        return ain, ain['value']
    if trig_type is 'averaged':
        return ain, ain['avg_value']
    if trig_type is 'filtered':
        return ain, ain['value'] # XXX
    assert False

def getAnalogTriggerInWindow(analog_trigger, status):
    status.value = 0
    ain, val = _get_trigger_value(analog_trigger)
    return val >= ain['trig_lower'] and val <= ain['trig_upper']
        
def getAnalogTriggerTriggerState(analog_trigger, status):
    # To work properly, this needs some other runtime component managing the
    # state variable too, but this works well enough
    status.value = 0
    ain, val = _get_trigger_value(analog_trigger)
    if val < ain['trig_lower']:
        ain['trig_state'] = False
        return False
    elif val > ain['trig_upper']:
        ain['trig_state'] = True
        return True
    else:
        return ain['trig_state']

def getAnalogTriggerOutput(analog_trigger, type, status):
    if type == constants.AnalogTriggerType.kInWindow:
        return getAnalogTriggerInWindow(analog_trigger, status)
    if type == constants.AnalogTriggerType.kState:
        return getAnalogTriggerTriggerState(analog_trigger, status)
    else:
        status.value = ANALOG_TRIGGER_PULSE_OUTPUT_ERROR
        return False


#############################################################################
# Compressor
#############################################################################

def initializeCompressor(module):
    assert module == 0 # don't support multiple modules for now
    hal_data['compressor'] = dict(enabled=True)
    return types.PCM(module)

def checkCompressorModule(module):
    return module < 63

def getCompressor(pcm, status):
    status.value = 0
    return hal_data['compressor']['enabled']

def setClosedLoopControl(pcm, value, status):
    status.value = 0
    hal_data['compressor']['closed_loop_enabled'] = value

def getClosedLoopControl(pcm, status):
    status.value = 0
    return hal_data['compressor']['closed_loop_enabled']

def getPressureSwitch(pcm, status):
    status.value = 0
    return hal_data['compressor']['pressure_switch']

def getCompressorCurrent(pcm, status):
    status.value = 0
    return hal_data['compressor']['current']


#############################################################################
# Digital
#############################################################################

kExpectedLoopTiming = 40
kDigitalPins = 26
kPwmPins = 20
kRelayPins = 8
kNumHeaders = 10

def initializeDigitalPort(port, status):
    status.value = 0
    return types.DigitalPort(port)

def checkPWMChannel(digital_port):
    return digital_port.pin < kPwmPins

def checkRelayChannel(digital_port):
    return digital_port.pin < kRelayPins

#
# PWM
#

def setPWM(digital_port, value, status):
    status.value = 0
    hal_data['pwm'][digital_port.pin]['value'] = value

def allocatePWMChannel(digital_port, status):
    status.value = 0
    if hal_data['pwm'][digital_port.pin]['initialized']:
        return False
    
    hal_data['pwm'][digital_port.pin]['initialized'] = True
    return True

def freePWMChannel(digital_port, status):
    status.value = 0
    assert hal_data['pwm'][digital_port.pin]['initialized']
    hal_data['pwm'][digital_port.pin]['initialized'] = False
    hal_data['pwm'][digital_port.pin]['value'] = 0
    hal_data['pwm'][digital_port.pin]['period_scale'] = None
    hal_data['pwm'][digital_port.pin]['zero_latch'] = False

def getPWM(digital_port, status):
    status.value = 0
    return hal_data['pwm'][digital_port.pin]['value']

def latchPWMZero(digital_port, status):
    # TODO: what does this do?
    status.value = 0
    hal_data['pwm'][digital_port.pin]['zero_latch'] = True

def setPWMPeriodScale(digital_port, squelch_mask, status):
    status.value = 0
    hal_data['pwm'][digital_port.pin]['period_scale'] = squelch_mask

#
# DIO PWM
#

def allocatePWM(status):
    status.value = 0
    
    for i, v in enumerate(hal_data['d0_pwm']):
        if v is None:
            break
    else:
        return None
    
    hal_data['d0_pwm'][i] = {'duty_cycle': None, 'pin': None}
    return types.PWM(i)

def freePWM(pwm, status):
    status.value = 0
    hal_data['d0_pwm'][pwm.idx] = None
    
def setPWMRate(rate, status):
    status.value = 0
    hal_data['d0_pwm_rate'] = rate

def setPWMDutyCycle(pwm, duty_cycle, status):
    status.value = 0
    hal_data['d0_pwm'][pwm.idx]['duty_cycle'] = duty_cycle

def setPWMOutputChannel(pwm, pin, status):
    status.value = 0
    hal_data['d0_pwm'][pwm.idx]['pin'] = pin

#
# Relay
#

def setRelayForward(digital_port, on, status):
    status.value = 0
    hal_data['relay'][digital_port.pin]['fwd'] = on

def setRelayReverse(digital_port, on, status):
    status.value = 0
    hal_data['relay'][digital_port.pin]['rev'] = on

def getRelayForward(digital_port, status):
    return hal_data['relay'][digital_port.pin]['fwd']

def getRelayReverse(digital_port, status):
    status.value = 0
    return hal_data['relay'][digital_port.pin]['rev']

#
# DIO
#

def allocateDIO(digital_port, input, status):
    status.value = 0
    if hal_data['dio'][digital_port.pin] is not None:
        return False
    hal_data['dio'][digital_port.pin] = {'value': 0, 'pulse_length': None, 'is_input': input }

def freeDIO(digital_port, status):
    status.value = 0
    hal_data['dio'][digital_port.pin] = None

def setDIO(digital_port, value, status):
    status.value = 0
    hal_data['dio'][digital_port.pin]['value'] = 1 if value else 0

def getDIO(digital_port, status):
    status.value = 0
    return hal_data['dio'][digital_port.pin]['value']

def getDIODirection(digital_port, status):
    status.value = 0
    return hal_data['dio'][digital_port.pin]['is_input']

def pulse(digital_port, pulse_length, status):
    status.value = 0
    hal_data['dio'][digital_port.pin]['pulse_length'] = pulse_length

def isPulsing(digital_port, status):
    status.value = 0
    return hal_data['dio'][digital_port.pin]['pulse_length'] is not None

def isAnyPulsing(status):
    status.value = 0
    
    for p in hal_data['dio']:
        if p is not None and p['pulse_length'] is not None:
            return True
    return False
    

#
# Counter
#

def initializeCounter(mode, status):
    status.value = 0
    for idx in range(0, len(hal_data['counter'])):
        cnt = hal_data['counter'][idx]
        if cnt['initialized'] == False:
            cnt['initialized'] = True
            cnt['mode'] = mode
            return types.Counter(idx), idx 
    
    status.value = NO_AVAILABLE_RESOURCES
    return None, -1


def freeCounter(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['initialized'] = False

def setCounterAverageSize(counter, size, status):
    status.value = 0
    hal_data['counter'][counter.idx]['average_size'] = size

def setCounterUpSource(counter, pin, analog_trigger, status):
    status.value = 0
    hal_data['counter'][counter.idx]['up_source_channel'] = pin
    hal_data['counter'][counter.idx]['up_source_trigger'] = analog_trigger
    
    if hal_data['counter'][counter.idx]['mode'] in \
       [constants.Mode.kTwoPulse, constants.Mode.kExternalDirection]:
        setCounterUpSourceEdge(counter, True, False, status) 

def setCounterUpSourceEdge(counter, rising_edge, falling_edge, status):
    status.value = 0
    hal_data['counter'][counter.idx]['up_rising_edge'] = rising_edge
    hal_data['counter'][counter.idx]['up_falling_edge'] = falling_edge

def clearCounterUpSource(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['up_rising_edge'] = False
    hal_data['counter'][counter.idx]['up_falling_edge'] = False
    hal_data['counter'][counter.idx]['up_source_channel'] = 0
    hal_data['counter'][counter.idx]['up_source_trigger'] = False

def setCounterDownSource(counter, pin, analog_trigger, status):
    status.value = 0
    if hal_data['counter'][counter.idx]['mode'] not in \
       [constants.Mode.kTwoPulse, constants.Mode.kExternalDirection]:
        status.value = PARAMETER_OUT_OF_RANGE
        return
    
    hal_data['counter'][counter.idx]['down_source_channel'] = pin
    hal_data['counter'][counter.idx]['down_source_trigger'] = analog_trigger
    

def setCounterDownSourceEdge(counter, rising_edge, falling_edge, status):
    status.value = 0
    hal_data['counter'][counter.idx]['down_rising_edge'] = rising_edge
    hal_data['counter'][counter.idx]['down_falling_edge'] = falling_edge

def clearCounterDownSource(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['down_rising_edge'] = False
    hal_data['counter'][counter.idx]['down_falling_edge'] = False
    hal_data['counter'][counter.idx]['down_source_channel'] = 0
    hal_data['counter'][counter.idx]['down_source_trigger'] = False

def setCounterUpDownMode(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['mode'] = constants.Mode.kTwoPulse

def setCounterExternalDirectionMode(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['mode'] = constants.Mode.kExternalDirection

def setCounterSemiPeriodMode(counter, high_semi_period, status):
    status.value = 0
    hal_data['counter'][counter.idx]['mode'] = constants.Mode.kSemiperiod
    hal_data['counter'][counter.idx]['up_rising_edge'] = high_semi_period
    hal_data['counter'][counter.idx]['update_when_empty'] = False

def setCounterPulseLengthMode(counter, threshold, status):
    hal_data['counter'][counter.idx]['mode'] = constants.Mode.kPulseLength
    hal_data['counter'][counter.idx]['pulse_length_threshold'] = threshold

def getCounterSamplesToAverage(counter, status):
    status.value = 0
    return hal_data['counter'][counter.idx]['samples_to_average']

def setCounterSamplesToAverage(counter, samples_to_average, status):
    status.value = 0
    hal_data['counter'][counter.idx]['samples_to_average'] = samples_to_average

def resetCounter(counter, status):
    status.value = 0
    hal_data['counter'][counter.idx]['count'] = 0

def getCounter(counter, status):
    status.value = 0
    return hal_data['counter'][counter.idx]['count']

def getCounterPeriod(counter, status):
    status.value = 0
    return hal_data['counter'][counter.idx]['period']

def setCounterMaxPeriod(counter, max_period, status):
    status.value = 0
    hal_data['counter'][counter.idx]['max_period'] = max_period

def setCounterUpdateWhenEmpty(counter, enabled, status):
    status.value = 0
    hal_data['counter'][counter.idx]['update_when_empty'] = enabled

def getCounterStopped(counter, status):
    status.value = 0
    cnt = hal_data['counter'][counter.idx]
    return cnt['period'] > cnt['max_period']

def getCounterDirection(counter, status):
    status.value = 0
    return hal_data['counter'][counter.idx]['direction']

def setCounterReverseDirection(counter, reverse_direction, status):
    status.value = 0
    hal_data['counter'][counter.idx]['reverse_direction'] = reverse_direction

#
# Encoder
#

def initializeEncoder(port_a_module, port_a_pin, port_a_analog_trigger, port_b_module, port_b_pin, port_b_analog_trigger, reverse_direction, status):
    status.value = 0
    for idx in range(0, len(hal_data['encoder'])):
        enc = hal_data['encoder'][idx]
        if enc['initialized'] == False:
            enc['initialized'] = True
            enc['config'] = [port_a_module, port_a_pin, port_a_analog_trigger, port_b_module, port_b_pin, port_b_analog_trigger]
            enc['reverse_direction'] = reverse_direction
            return types.Encoder(idx), idx 
        
    # I think HAL fails silently.. 
    status.value = NO_AVAILABLE_RESOURCES
    return None, -1

def freeEncoder(encoder, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['initialized'] = False

def resetEncoder(encoder, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['count'] = 0

def getEncoder(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['count']

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

def setEncoderReverseDirection(encoder, reverse_direction, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['reverse_direction'] = reverse_direction

def setEncoderSamplesToAverage(encoder, samples_to_average, status):
    status.value = 0
    hal_data['encoder'][encoder.idx]['samples_to_average'] = samples_to_average

def getEncoderSamplesToAverage(encoder, status):
    status.value = 0
    return hal_data['encoder'][encoder.idx]['samples_to_average']

def getLoopTiming(status):
    status.value = 0
    return hal_data['pwm_loop_timing']

#
# SPI
#

def spiInitialize(port, status):
    assert False

def spiTransaction(port, data_to_send, data_received, size):
    assert False

def spiWrite(port, data_to_send, send_size):
    assert False

def spiRead(port, buffer, count):
    assert False

def spiClose(port):
    assert False

def spiSetSpeed(port, speed):
    assert False

def spiSetOpts(port, msb_first, sample_on_trailing, clk_idle_high):
    assert False

def spiSetChipSelectActiveHigh(port, status):
    assert False

def spiSetChipSelectActiveLow(port, status):
    assert False

def spiGetHandle(port):
    assert False

def spiSetHandle(port, handle):
    assert False

def spiGetSemaphore(port):
    assert False

def spiSetSemaphore(port, semaphore):
    assert False

#
# i2c
#

def i2CInitialize(port, status):
    assert False

def i2CTransaction(port, device_address, data_to_send, send_size, data_received, receive_size):
    assert False

def i2CWrite(port, device_address, data_to_send, send_size):
    assert False

def i2CRead(port, device_address, buffer, count):
    assert False

def i2CClose(port):
    assert False


#############################################################################
# Interrupts
#############################################################################

def initializeInterrupts(interrupt_index, watcher, status):
    assert False # TODO

def cleanInterrupts(interrupt, status):
    assert False # TODO

def waitForInterrupt(interrupt, timeout, ignorePrevious, status):
    assert False # TODO

def enableInterrupts(interrupt, status):
    assert False # TODO

def disableInterrupts(interrupt, status):
    assert False # TODO

def readRisingTimestamp(interrupt, status):
    assert False # TODO

def readFallingTimestamp(interrupt, status):
    assert False # TODO

def requestInterrupts(interrupt, routing_module, routing_pin, routing_analog_trigger, status):
    assert False # TODO

def attachInterruptHandler(interrupt, handler, param, status):
    assert False # TODO

def setInterruptUpSourceEdge(interrupt, rising_edge, falling_edge, status):
    assert False # TODO


#############################################################################
# Notifier
#############################################################################

def initializeNotifier(processQueue, status):
    assert False # TODO

def cleanNotifier(notifier, status):
    assert False # TODO

def updateNotifierAlarm(notifier, triggerTime, status):
    assert False # TODO


#############################################################################
# PDP
#############################################################################

def getPDPTemperature(status):
    status.value = 0
    return hal_data['pdp']['temperature']

def getPDPVoltage(status):
    status.value = 0
    return hal_data['pdp']['voltage']

def getPDPChannelCurrent(channel, status):
    if channel < 0 or channel >= len(hal_data['pdp']['current']):
        status.value = CTR_InvalidParamValue
        return 0
    status.value = 0
    return hal_data['pdp']['current'][channel]


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
# Solenoid
#############################################################################

def initializeSolenoidPort(port, status):
    status.value = 0
    # sigh: it would be nice if all the solenoids weren't always initialized
    hal_data['solenoid'][port.pin] = False 
    return types.SolenoidPort(port)

def checkSolenoidModule(module):
    return module < 63

def getSolenoid(solenoid_port, status):
    status.value = 0
    return hal_data['solenoid'][solenoid_port.pin]

def setSolenoid(solenoid_port, value, status):
    status.value = 0
    hal_data['solenoid'][solenoid_port.pin] = value


#############################################################################
# Utilities
#############################################################################

HAL_NO_WAIT = 0
HAL_WAIT_FOREVER = -1

def delayTicks(ticks):
    # ticks is ns*3? don't use this.
    assert False

def delayMillis(ms):
    time.sleep(1000*ms)

def delaySeconds(s):
    time.sleep(s)

#############################################################################
# CAN
#############################################################################

def FRC_NetworkCommunication_CANSessionMux_sendMessage(messageID, data, dataSize, periodMs, status):
    assert False

def FRC_NetworkCommunication_CANSessionMux_receiveMessage(messageID, messageIDMask, data, status):
    assert False # returns dataSize, timeStamp

def FRC_NetworkCommunication_CANSessionMux_openStreamSession(messageID, messageIDMask, maxMessages, status):
    assert False # returns sessionHandle

def FRC_NetworkCommunication_CANSessionMux_closeStreamSession(sessionHandle):
    assert False

def FRC_NetworkCommunication_CANSessionMux_readStreamSession(sessionHandle, messages, messagesToRead, status):
    assert False # returns messagesRead

def FRC_NetworkCommunication_CANSessionMux_getCANStatus(status):
    assert False # returns all params

