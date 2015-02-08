
from hal import constants
from . import types

import threading

from . import data
from .data import hal_data
from hal_impl.sim_hooks import SimHooks
from hal_impl.pwm_helpers import reverseByType

import logging
logger = logging.getLogger('hal')

hooks = SimHooks()

def reset_hal():
    data._reset_hal_data(hooks)

reset_hal()

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
    with sem.cond:
        sem.cond.wait() # timeout is ignored in C++ HAL

def giveMultiWait(sem):
    with sem.cond:
        sem.cond.notify_all() # hal uses pthread_cond_broadcast, which wakes all threads


#############################################################################
# HAL
#############################################################################

def getPort(pin):
    return getPortWithModule(0, pin)

def getPortWithModule(module, pin):
    return types.Port(pin, module)

def _getHALErrorMessage(code):
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
    else:
        return "Unknown error status"
    
def getHALErrorMessage(code):
    return bytes(_getHALErrorMessage(code), 'utf-8')

def getFPGAVersion(status):
    status.value = 0
    return 2015

def getFPGARevision(status):
    status.value = 0
    return 0

def getFPGATime(status):
    status.value = 0
    return hooks.getFPGATime()

def getFPGAButton(status):
    status.value = 0
    return hal_data['fpga_button']

def HALSetErrorData(errors, errorsLength, wait_ms):
    logger.warn(errors.decode('utf-8').strip())
    hal_data['error_data'] = errors

def HALGetControlWord():
    return types.HALControlWord(hal_data['control'])

def HALGetAllianceStation():
    return hal_data['alliance_station']

def HALGetJoystickAxes(joystickNum, axes):
    # we store as -1 to 1 for ease of use, so convert to -128 to 127 here
    axes.axes = [int(a*128) if a < 0 else int(a*127) for a in hal_data['joysticks'][joystickNum]['axes']]
    axes.count = len(axes.axes)

def HALGetJoystickPOVs(joystickNum, povs):
    povs.povs = list(map(int, hal_data['joysticks'][joystickNum]['povs'][:]))
    povs.count = len(povs.povs)

def HALGetJoystickButtons(joystickNum, buttons):
    # buttons are stored as booleans for ease of use, convert to integer
    b = hal_data['joysticks'][joystickNum]['buttons']
    buttons.buttons = sum(int(v) << i for i, v in enumerate(b[1:]))
    buttons.count = len(b)-1

def HALGetJoystickDescriptor(joystickNum, descriptor):
    stick = hal_data["joysticks"][joystickNum]
    descriptor.isXbox = stick["isXbox"]
    descriptor.type = stick["type"]
    descriptor.name = stick["name"]
    descriptor.axisCount = stick["axisCount"]
    descriptor.buttonCount = stick["buttonCount"]

def HALSetJoystickOutputs(joystickNum, outputs, leftRumble, rightRumble):
    hal_data['joysticks'][joystickNum]["leftRumble"] = leftRumble
    hal_data['joysticks'][joystickNum]["rightRumble"] = rightRumble
    hal_data['joysticks'][joystickNum]["outputs"] = [bool(val) for val in bin(outputs)]

def HALGetMatchTime():
    '''
        Returns approximate match time:
        - At beginning of autonomous, time is 0
        - At beginning of teleop, time is set to 15
        - If robot is disabled, time is 0
    '''
    match_start = hal_data['time']['match_start']
    if match_start is None:
        return 0.0
    else:
        return (hooks.getFPGATime() - hal_data['time']['match_start'])/1000000.0

def HALGetSystemActive(status):
    status.value = 0
    return True

def HALGetBrownedOut(status):
    status.value = 0
    return False

def HALSetNewDataSem(sem):
    data.hal_newdata_sem = sem

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
    
    # TODO: Cover all interesting devices
    hur = constants.HALUsageReporting
    if resource ==  hur.kResourceType_Jaguar:
        hal_data['pwm'][instanceNumber]['type'] = 'jaguar'
    elif resource == hur.kResourceType_Talon:
        hal_data['pwm'][instanceNumber]['type'] = 'talon'
    elif resource == hur.kResourceType_TalonSRX:
        hal_data['pwm'][instanceNumber]['type'] = 'talonsrx'
    elif resource == hur.kResourceType_Victor:
        hal_data['pwm'][instanceNumber]['type'] = 'victor'
    elif resource == hur.kResourceType_VictorSP:
        hal_data['pwm'][instanceNumber]['type'] = 'victorsp'
    elif resource == hur.kResourceType_Solenoid:
        hal_data['solenoid'][instanceNumber]['initialized'] = True
    
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

def initializeAnalogOutputPort(port, status):
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

def initializeAnalogTrigger(port, status):
    status.value = 0
    for idx in range(0, len(hal_data['analog_trigger'])):
        cnt = hal_data['analog_trigger'][idx]
        if cnt['initialized'] == False:
            cnt['initialized'] = True
            cnt['port'] = port
            return types.AnalogTrigger(port, idx), idx

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
# Compressor
#############################################################################

def initializeCompressor(module):
    assert module == 0 # don't support multiple modules for now
    hal_data['compressor']['initialized'] = True
    return types.PCM(module)

def checkCompressorModule(module):
    return module < 63

def getCompressor(pcm, status):
    status.value = 0
    return hal_data['compressor']['on']

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

def getCompressorCurrentTooHighFault(pcm, status):
    status.value = 0
    return False

def getCompressorCurrentTooHighStickyFault(pcm, status):
    status.value = 0
    return False

def getCompressorShortedFault(pcm, status):
    status.value = 0
    return False

def getCompressorShortedStickyFault(pcm, status):
    status.value = 0
    return False

def getCompressorNotConnectedFault(pcm, status):
    status.value = 0
    return False

def getCompressorNotConnectedStickyFault(pcm, status):
    status.value = 0
    return False

def clearAllPCMStickyFaults(pcm, status):
    status.value = 0
    return False

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
# MXP
#

def remapMXPChannel(pin):
    return pin - 10

def remapMXPPWMChannel(pin):
    if pin < 14:
        return pin - 10
    else:
        return pin - 6

#
# PWM
#

def setPWM(digital_port, value, status):
    status.value = 0
    hal_data['pwm'][digital_port.pin]['raw_value'] = value
    hal_data['pwm'][digital_port.pin]['value'] = reverseByType(digital_port.pin)

def allocatePWMChannel(digital_port, status):
    status.value = 0

    if digital_port.pin >= kNumHeaders:
        mxp_port = remapMXPPWMChannel(digital_port.pin)
        if hal_data["mxp"][mxp_port]["initialized"]:
            status.value = RESOURCE_IS_ALLOCATED
            return False

    if hal_data['pwm'][digital_port.pin]['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return False
    
    hal_data['pwm'][digital_port.pin]['initialized'] = True

    if digital_port.pin >= kNumHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True

    return True

def freePWMChannel(digital_port, status):
    status.value = 0
    assert hal_data['pwm'][digital_port.pin]['initialized']
    hal_data['pwm'][digital_port.pin]['initialized'] = False
    hal_data['pwm'][digital_port.pin]['raw_value'] = 0
    hal_data['pwm'][digital_port.pin]['value'] = 0
    hal_data['pwm'][digital_port.pin]['period_scale'] = None
    hal_data['pwm'][digital_port.pin]['zero_latch'] = False

    if digital_port.pin >= kNumHeaders:
        mxp_port = remapMXPPWMChannel(digital_port.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False

def getPWM(digital_port, status):
    status.value = 0
    return hal_data['pwm'][digital_port.pin]['raw_value']

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
    relay = hal_data['relay'][digital_port.pin]
    relay['initialized'] = True
    relay['fwd'] = on

def setRelayReverse(digital_port, on, status):
    status.value = 0
    relay = hal_data['relay'][digital_port.pin]
    relay['initialized'] = True
    relay['rev'] = on

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
    if digital_port.pin >= kNumHeaders:
        mxp_port = remapMXPChannel(digital_port.pin)
        if hal_data["mxp"][mxp_port]["initialized"]:
            status.value = RESOURCE_IS_ALLOCATED
            return False
    dio = hal_data['dio'][digital_port.pin]
    if dio['initialized']:
        status.value = RESOURCE_IS_ALLOCATED
        return False
    if digital_port.pin >= kNumHeaders:
        hal_data["mxp"][mxp_port]["initialized"] = True
    dio['initialized'] = True
    dio['is_input'] = input


def freeDIO(digital_port, status):
    status.value = 0
    hal_data['dio'][digital_port.pin]['initialized'] = False
    if digital_port.pin >= kNumHeaders:
        mxp_port = remapMXPChannel(digital_port.pin)
        hal_data["mxp"][mxp_port]["initialized"] = False

def setDIO(digital_port, value, status):
    status.value = 0
    hal_data['dio'][digital_port.pin]['value'] = True if value else False

def getDIO(digital_port, status):
    status.value = 0
    return 1 if hal_data['dio'][digital_port.pin]['value'] else 0

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

            enc['config'] = {"ASource_Module": port_a_module, "ASource_Channel": port_a_pin, "ASource_AnalogTrigger": port_a_analog_trigger,
                             "BSource_Module": port_b_module, "BSource_Channel": port_b_pin, "BSource_AnalogTrigger": port_b_analog_trigger}
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

def setEncoderIndexSource(encoder, pin, analogTrigger, activeHigh, edgeSensitive, status):
    status.value = 0
    index_conf = {"IndexSource_Channel": pin, "IndexSource_Module": 0, "IndexSource_AnalogTrigger": analogTrigger,
                  "IndexActiveHigh": activeHigh, "IndexEdgeSensitive": edgeSensitive}
    hal_data['encoder'][encoder.idx]['config'].update(index_conf)

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

def getPDPTotalCurrent(status):
    status.value = 0
    return hal_data['pdp']['total_current']

def getPDPTotalPower(status):
    status.value = 0
    return hal_data['pdp']['total_power']

def getPDPTotalEnergy(status):
    status.value = 0
    return hal_data['pdp']['total_energy']

def resetPDPTotalEnergy(status):
    status.value = 0
    hal_data['pdp']['total_energy'] = 0

def clearPDPStickyFaults(status):
    status.value = 0
    # not sure what to do here?

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
    hal_data['solenoid'][port.pin]['value'] = False 
    return types.SolenoidPort(port)

def checkSolenoidModule(module):
    return module < 63

def getSolenoid(solenoid_port, status):
    status.value = 0
    return hal_data['solenoid'][solenoid_port.pin]['value']

def setSolenoid(solenoid_port, value, status):
    status.value = 0
    hal_data['solenoid'][solenoid_port.pin]['value'] = value

def getPCMSolenoidBlackList(solenoid_port, status):
    status.value = 0
    return 0

def getPCMSolenoidVoltageStickyFault(solenoid_port, status):
    status.value = 0
    return False

def getPCMSolenoidVoltageFault(solenoid_port, status):
    status.value = 0
    return False

def clearAllPCMStickyFaults_sol(solenoid_port, status):
    status.value = 0
    return False


#############################################################################
# TalonSRX
#############################################################################
def c_TalonSRX_Create(deviceNumber, controlPeriodMs):
    assert deviceNumber not in hal_data['CAN']
    
    hal_data['CAN'][deviceNumber] = data.NotifyDict({
        'type': 'talonsrx',
        'value': 0,
        'params': data.NotifyDict({}), # key is param, value is the value
        'fault_overtemp': 0,
        'fault_undervoltage': 0,
        'fault_forlim': 0,
        'fault_revlim': 0,
        'fault_hwfailure': 0,
        'fault_forsoftlim': 0,
        'fault_revsoftlim': 0,
        'stickyfault_overtemp': 0,
        'stickyfault_undervoltage': 0,
        'stickyfault_forlim': 0,
        'stickyfault_revlim': 0,
        'stickyfault_forsoftlim': 0,
        'stickyfault_revsoftlim': 0,
        'applied_throttle': 0,
        'closeloop_err': 0,
        'feedback_device_select': 0,
        'mode_select': 0,
        'limit_switch_en': 0,
        'limit_switch_closed_for': 0,
        'limit_switch_closed_rev': 0,
        'sensor_position': 0,
        'sensor_velocity': 0,
        'current': 0,
        'brake_enabled': 0,
        'enc_position': 0,
        'enc_velocity': 0,
        'enc_index_rise_events': 0,
        'quad_apin': 0,
        'quad_bpin': 0,
        'quad_idxpin': 0,
        'analog_in_with_ov': 0,
        'analog_in_vel': 0,
        'temp': 0,
        'battery': 0,
        'reset_count': 0,
        'reset_flags': 0,
        'firmware_version': 0,
        'override_limit_switch': 0,
        
        'feedback_device': None,
        'rev_motor_during_close_loop': None,
        'override_braketype': None,
        'profile_slot_select': None,
        'ramp_throttle': None,
        'rev_feedback_sensor': None
        
    })
    
    return types.TalonSRX(deviceNumber)
    

def c_TalonSRX_Destroy(handle):
    del hal_data['CAN'][handle.id]

def c_TalonSRX_SetParam(handle, paramEnum, value):
    hal_data['CAN'][handle.id]['params'][paramEnum] = value

def c_TalonSRX_RequestParam(handle, paramEnum):
    params = hal_data['CAN'][handle.id]['params']
    assert paramEnum in params, "Parameter %s not set!" % constants.TalonSRXParam_tostr[paramEnum] # TODO: is this correct?
    return params[paramEnum]

def c_TalonSRX_GetParamResponse(handle, paramEnum):
    params = hal_data['CAN'][handle.id]['params']
    assert paramEnum in params, "Parameter %s not set!" % constants.TalonSRXParam_tostr[paramEnum] # TODO: is this correct?
    return params[paramEnum]

def c_TalonSRX_GetParamResponseInt32(handle, paramEnum):
    params = hal_data['CAN'][handle.id]['params']
    assert paramEnum in params, "Parameter %s not set!" % constants.TalonSRXParam_tostr[paramEnum] # TODO: is this correct?
    return params[paramEnum]

def c_TalonSRX_SetStatusFrameRate(handle, frameEnum, periodMs):
    pass

def c_TalonSRX_ClearStickyFaults(handle):
    hal_data['CAN'][handle.id]['sticky_overtemp'] = 0
    hal_data['CAN'][handle.id]['stickyfault_undervoltage'] = 0
    hal_data['CAN'][handle.id]['stickyfault_forlim'] = 0
    hal_data['CAN'][handle.id]['stickyfault_revlim'] = 0
    hal_data['CAN'][handle.id]['stickyfault_forsoftlim'] = 0
    hal_data['CAN'][handle.id]['stickyfault_revsoftlim'] = 0

def c_TalonSRX_GetFault_OverTemp(handle):
    return hal_data['CAN'][handle.id]['fault_overtemp']

def c_TalonSRX_GetFault_UnderVoltage(handle):
    return hal_data['CAN'][handle.id]['fault_undervoltage']

def c_TalonSRX_GetFault_ForLim(handle):
    return hal_data['CAN'][handle.id]['fault_forlim']

def c_TalonSRX_GetFault_RevLim(handle):
    return hal_data['CAN'][handle.id]['fault_revlim']

def c_TalonSRX_GetFault_HardwareFailure(handle):
    return hal_data['CAN'][handle.id]['fault_hwfailure']

def c_TalonSRX_GetFault_ForSoftLim(handle):
    return hal_data['CAN'][handle.id]['fault_forsoftlim']

def c_TalonSRX_GetFault_RevSoftLim(handle):
    return hal_data['CAN'][handle.id]['fault_revsoftlim']

def c_TalonSRX_GetStckyFault_OverTemp(handle):
    return hal_data['CAN'][handle.id]['stickyfault_overtemp']

def c_TalonSRX_GetStckyFault_UnderVoltage(handle):
    return hal_data['CAN'][handle.id]['stickyfault_undervoltage']

def c_TalonSRX_GetStckyFault_ForLim(handle):
    return hal_data['CAN'][handle.id]['stickyfault_forlim']

def c_TalonSRX_GetStckyFault_RevLim(handle):
    return hal_data['CAN'][handle.id]['stickyfault_revlim']

def c_TalonSRX_GetStckyFault_ForSoftLim(handle):
    return hal_data['CAN'][handle.id]['stickyfault_forsoftlim']

def c_TalonSRX_GetStckyFault_RevSoftLim(handle):
    return hal_data['CAN'][handle.id]['stickyfault_revsoftlim']

def c_TalonSRX_GetAppliedThrottle(handle):
    return hal_data['CAN'][handle.id]['applied_throttle']

def c_TalonSRX_GetCloseLoopErr(handle):
    return hal_data['CAN'][handle.id]['closeloop_err']

def c_TalonSRX_GetFeedbackDeviceSelect(handle):
    return hal_data['CAN'][handle.id]['feedback_device_select']

def c_TalonSRX_GetModeSelect(handle):
    return hal_data['CAN'][handle.id]['mode_select']

def c_TalonSRX_GetLimitSwitchEn(handle):
    return hal_data['CAN'][handle.id]['limit_switch_en']

def c_TalonSRX_GetLimitSwitchClosedFor(handle):
    return hal_data['CAN'][handle.id]['limit_switch_closed_for']

def c_TalonSRX_GetLimitSwitchClosedRev(handle):
    return hal_data['CAN'][handle.id]['limit_switch_closed_rev']

def c_TalonSRX_GetSensorPosition(handle):
    return hal_data['CAN'][handle.id]['sensor_position']

def c_TalonSRX_GetSensorVelocity(handle):
    return hal_data['CAN'][handle.id]['sensor_velocity']

def c_TalonSRX_GetCurrent(handle):
    return hal_data['CAN'][handle.id]['current']

def c_TalonSRX_GetBrakeIsEnabled(handle):
    return hal_data['CAN'][handle.id]['brake_enabled']

def c_TalonSRX_GetEncPosition(handle):
    return hal_data['CAN'][handle.id]['enc_position']

def c_TalonSRX_GetEncVel(handle):
    return hal_data['CAN'][handle.id]['enc_velocity']

def c_TalonSRX_GetEncIndexRiseEvents(handle):
    return hal_data['CAN'][handle.id]['enc_index_rise_events']

def c_TalonSRX_GetQuadApin(handle):
    return hal_data['CAN'][handle.id]['quad_apin']

def c_TalonSRX_GetQuadBpin(handle):
    return hal_data['CAN'][handle.id]['quad_bpin']

def c_TalonSRX_GetQuadIdxpin(handle):
    return hal_data['CAN'][handle.id]['quad_idxpin']

def c_TalonSRX_GetAnalogInWithOv(handle):
    return hal_data['CAN'][handle.id]['analog_in_with_ov']

def c_TalonSRX_GetAnalogInVel(handle):
    return hal_data['CAN'][handle.id]['analog_in_vel']

def c_TalonSRX_GetTemp(handle):
    return hal_data['CAN'][handle.id]['temp']

def c_TalonSRX_GetBatteryV(handle):
    return hal_data['CAN'][handle.id]['battery']

def c_TalonSRX_GetResetCount(handle):
    return hal_data['CAN'][handle.id]['reset_count']

def c_TalonSRX_GetResetFlags(handle):
    return hal_data['CAN'][handle.id]['reset_flags']

def c_TalonSRX_GetFirmVers(handle):
    return hal_data['CAN'][handle.id]['firmware_version']

def c_TalonSRX_SetDemand(handle, param):
    hal_data['CAN'][handle.id]['value'] = param

def c_TalonSRX_SetOverrideLimitSwitchEn(handle, param):
    hal_data['CAN'][handle.id]['override_limit_switch'] = param

def c_TalonSRX_SetFeedbackDeviceSelect(handle, param):
    hal_data['CAN'][handle.id]['feedback_device'] = param

def c_TalonSRX_SetRevMotDuringCloseLoopEn(handle, param):
    hal_data['CAN'][handle.id]['rev_motor_during_close_loop'] = param

def c_TalonSRX_SetOverrideBrakeType(handle, param):
    hal_data['CAN'][handle.id]['override_braketype'] = param

def c_TalonSRX_SetModeSelect(handle, param):
    hal_data['CAN'][handle.id]['mode_select'] = param

def c_TalonSRX_SetModeSelect2(handle, modeSelect, demand):
    hal_data['CAN'][handle.id]['mode_select'] = modeSelect
    hal_data['CAN'][handle.id]['value'] = demand

def c_TalonSRX_SetProfileSlotSelect(handle, param):
    hal_data['CAN'][handle.id]['profile_slot_select'] = param

def c_TalonSRX_SetRampThrottle(handle, param):
    hal_data['CAN'][handle.id]['ramp_throttle'] = param

def c_TalonSRX_SetRevFeedbackSensor(handle, param):
    hal_data['CAN'][handle.id]['rev_feedback_sensor'] = param

#############################################################################
# Utilities
#############################################################################

HAL_NO_WAIT = 0
HAL_WAIT_FOREVER = -1

def delayTicks(ticks):
    # ticks is ns*3? don't use this.
    assert False

def delayMillis(ms):
    hooks.delayMillis(ms)

def delaySeconds(s):
    hooks.delaySeconds(s)

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

