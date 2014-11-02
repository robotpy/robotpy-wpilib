
#
# TODO: organize imports... I think this needs the structs that are in hal, but
# hal needs the funcs in here... 
#

# TODO: actually implement this

from . import types

import time
import threading

hal_data = {
    # don't fill this out, fill out the version in _reset_hal_data
}


def _reset_hal_data():
    '''Intended to be used by the test runner'''
    global hal_data
    hal_data = {
        'accelerometer': {
            'active': False,
            'range': 0,
            'x': 0,
            'y': 0,
            'z': 0
        },
                
        'power': {
            'vin_voltage': 0,
            'vin_current': 0,
            'user_voltage_6v': 6.0,
            'user_current_6v': 0,
            'user_voltage_5v': 5.0,
            'user_current_5v': 0,
            'user_voltage_3v3': 3.3,
            'user_current_3v3': 0
        },
                
        'solenoid': [None]*8,
                
        'pdp': {
            'temperature': 0,
            'voltage': 0,
            'current': [0]*16
        }
    }

_reset_hal_data()

#
# Misc constants
#

CTR_InvalidParamValue = 3


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

def takeMultiWait(sem, timeout):
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
    assert False # TODO

def getFPGAVersion(status):
    status.value = 0
    return 2015

def getFPGARevision(status):
    status.value = 0
    return 0

def getFPGATime(status):
    assert False

def getFPGAButton(status):
    assert False

def HALSetErrorData(errors, errorsLength, wait_ms):
    assert False

def HALGetControlWord():
    assert False

def HALGetAllianceStation():
    assert False

def HALGetJoystickAxes(joystickNum, axes):
    assert False

def HALGetJoystickPOVs(joystickNum, povs):
    assert False

def HALGetJoystickButtons(joystickNum, buttons, count):
    assert False

def HALSetNewDataSem(sem):
    assert False

def HALInitialize(mode=0):
    assert False

def HALNetworkCommunicationObserveUserProgramStarting():
    assert False

def HALNetworkCommunicationObserveUserProgramDisabled():
    assert False

def HALNetworkCommunicationObserveUserProgramAutonomous():
    assert False

def HALNetworkCommunicationObserveUserProgramTeleop():
    assert False

def HALNetworkCommunicationObserveUserProgramTest():
    assert False

def HALReport(resource, instanceNumber, context=0, feature=None):
    pass


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

def initializeAnalogOutputPort(port, status):
    assert False

def setAnalogOutput(analog_port, voltage, status):
    assert False

def getAnalogOutput(analog_port, status):
    assert False

def checkAnalogOutputChannel(pin):
    assert False

def initializeAnalogInputPort(port, status):
    assert False

def checkAnalogModule(module):
    assert False

def checkAnalogInputChannel(pin):
    assert False

def setAnalogSampleRate(samples_per_second, status):
    assert False

def getAnalogSampleRate(status):
    assert False

def setAnalogAverageBits(analog_port, bits, status):
    assert False

def getAnalogAverageBits(analog_port, status):
    assert False

def setAnalogOversampleBits(analog_port, bits, status):
    assert False

def getAnalogOversampleBits(analog_port, status):
    assert False

def getAnalogValue(analog_port, status):
    assert False

def getAnalogAverageValue(analog_port, status):
    assert False

def getAnalogVoltsToValue(analog_port, voltage, status):
    assert False

def getAnalogVoltage(analog_port, status):
    assert False

def getAnalogAverageVoltage(analog_port, status):
    assert False

def getAnalogLSBWeight(analog_port, status):
    assert False

def getAnalogOffset(analog_port, status):
    assert False

def isAccumulatorChannel(analog_port, status):
    assert False

def initAccumulator(analog_port, status):
    assert False

def resetAccumulator(analog_port, status):
    assert False

def setAccumulatorCenter(analog_port, status):
    assert False

def setAccumulatorDeadband(analog_port, deadband, status):
    assert False

def getAccumulatorValue(analog_port, status):
    assert False

def getAccumulatorCount(analog_port, status):
    assert False

def getAccumulatorOutput(analog_port, status):
    assert False

def initializeAnalogTrigger(port, status):
    assert False

def cleanAnalogTrigger(analog_trigger, status):
    assert False

def setAnalogTriggerLimitsRaw(analog_trigger, lower, upper, status):
    assert False

def setAnalogTriggerLimitsVoltage(analog_trigger, lower, upper, status):
    assert False

def setAnalogTriggerAveraged(analog_trigger, use_averaged_value, status):
    assert False

def setAnalogTriggerFiltered(analog_trigger, use_filtered_value, status):
    assert False

def getAnalogTriggerInWindow(analog_trigger, status):
    assert False

def getAnalogTriggerTriggerState(analog_trigger, status):
    assert False

def getAnalogTriggerOutput(analog_trigger, type, status):
    assert False


#############################################################################
# Compressor
#############################################################################

def initializeCompressor(module):
    assert False

def checkCompressorModule(module):
    assert False

def getCompressor(pcm, status):
    assert False

def setClosedLoopControl(pcm, value, status):
    assert False

def getClosedLoopControl(pcm, status):
    assert False

def getPressureSwitch(pcm, status):
    assert False

def getCompressorCurrent(pcm, status):
    assert False


#############################################################################
# Digital
#############################################################################

def initializeDigitalPort(port, status):
    assert False

def checkPWMChannel(digital_port):
    assert False

def checkRelayChannel(digital_port):
    assert False

def setPWM(digital_port, value, status):
    assert False

def allocatePWMChannel(digital_port, status):
    assert False

def freePWMChannel(digital_port, status):
    assert False

def getPWM(digital_port, status):
    assert False

def latchPWMZero(digital_port, status):
    assert False

def setPWMPeriodScale(digital_port, squelch_mask, status):
    assert False

def allocatePWM(status):
    assert False

def freePWM(pwm, status):
    assert False

def setPWMRate(rate, status):
    assert False

def setPWMDutyCycle(pwm, duty_cycle, status):
    assert False

def setPWMOutputChannel(pwm, pin, status):
    assert False

def setRelayForward(digital_port, on, status):
    assert False

def setRelayReverse(digital_port, on, status):
    assert False

def getRelayForward(digital_port, status):
    assert False

def getRelayReverse(digital_port, status):
    assert False

def allocateDIO(digital_port, input, status):
    assert False

def freeDIO(digital_port, status):
    assert False

def setDIO(digital_port, value, status):
    assert False

def getDIO(digital_port, status):
    assert False

def getDIODirection(digital_port, status):
    assert False

def pulse(digital_port, pulse_length, status):
    assert False

def isPulsing(digital_port, status):
    assert False

def isAnyPulsing(status):
    assert False

def initializeCounter(mode, status):
    assert False

def freeCounter(counter, status):
    assert False

def setCounterAverageSize(counter, size, status):
    assert False

def setCounterUpSource(counter, pin, analog_trigger, status):
    assert False

def setCounterUpSourceEdge(counter, rising_edge, falling_edge, status):
    assert False

def clearCounterUpSource(counter, status):
    assert False

def setCounterDownSource(counter, pin, analog_trigger, status):
    assert False

def setCounterDownSourceEdge(counter, rising_edge, falling_edge, status):
    assert False

def clearCounterDownSource(counter, status):
    assert False

def setCounterUpDownMode(counter, status):
    assert False

def setCounterExternalDirectionMode(counter, status):
    assert False

def setCounterSemiPeriodMode(counter, high_semi_period, status):
    assert False

def setCounterPulseLengthMode(counter, threshold, status):
    assert False

def getCounterSamplesToAverage(counter, status):
    assert False

def setCounterSamplesToAverage(counter, samples_to_average, status):
    assert False

def resetCounter(counter, status):
    assert False

def getCounter(counter, status):
    assert False

def getCounterPeriod(counter, status):
    assert False

def setCounterMaxPeriod(counter, max_period, status):
    assert False

def setCounterUpdateWhenEmpty(counter, enabled, status):
    assert False

def getCounterStopped(counter, status):
    assert False

def getCounterDirection(counter, status):
    assert False

def setCounterReverseDirection(counter, reverse_direction, status):
    assert False

def initializeEncoder(port_a_module, port_a_pin, port_a_analog_trigger, port_b_module, port_b_pin, port_b_analog_trigger, reverse_direction, status):
    assert False

def freeEncoder(encoder, status):
    assert False

def resetEncoder(encoder, status):
    assert False

def getEncoder(encoder, status):
    assert False

def getEncoderPeriod(encoder, status):
    assert False

def setEncoderMaxPeriod(encoder, max_period, status):
    assert False

def getEncoderStopped(encoder, status):
    assert False

def getEncoderDirection(encoder, status):
    assert False

def setEncoderReverseDirection(encoder, reverse_direction, status):
    assert False

def setEncoderSamplesToAverage(encoder, samples_to_average, status):
    assert False

def getEncoderSamplesToAverage(encoder, status):
    assert False

def getLoopTiming(status):
    assert False

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

def getUserVoltage5V(status):
    status.value = 0
    return hal_data['power']['user_voltage_5v']

def getUserCurrent5V(status):
    status.value = 0
    return hal_data['power']['user_current_5v']

def getUserVoltage3V3(status):
    status.value = 0
    return hal_data['power']['user_voltage_3v3']

def getUserCurrent3V3(status):
    status.value = 0
    return hal_data['power']['user_current_3v3']

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

