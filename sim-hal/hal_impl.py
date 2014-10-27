
#
# TODO: organize imports... I think this needs the structs that are in hal, but
# hal needs the funcs in here... 
#

# TODO: actually implement this


# TODO: define the structure of this thing
hal_data = {
}


def _reset_hal_data():
    '''Intended to be used by the test runner'''
    global hal_data
    hal_data = {
    }

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
    pass

def initializeMutexNormal():
    pass

def deleteMutex(sem):
    pass

def takeMutex(sem):
    pass

def tryTakeMutex(sem):
    pass

def giveMutex(sem):
    pass

def initializeSemaphore(initial_value):
    pass

def deleteSemaphore(sem):
    pass

def takeSemaphore(sem):
    pass

def tryTakeSemaphore(sem):
    pass

def giveSemaphore(sem):
    pass

def initializeMultiWait():
    pass

def deleteMultiWait(sem):
    pass

def takeMultiWait(sem, timeout):
    pass

def giveMultiWait(sem):
    pass



#############################################################################
# HAL
#############################################################################

def getPort(pin):
    pass

def getPortWithModule(module, pin):
    pass

def getHALErrorMessage(code):
    pass

def getFPGAVersion(status):
    pass

def getFPGARevision(status):
    pass

def getFPGATime(status):
    pass

def getFPGAButton(status):
    pass

def HALSetErrorData(errors, errorsLength, wait_ms):
    pass

def HALGetControlWord():
    pass

def HALGetAllianceStation():
    pass

def HALGetJoystickAxes(joystickNum, axes):
    pass

def HALGetJoystickPOVs(joystickNum, povs):
    pass

def HALGetJoystickButtons(joystickNum, buttons, count):
    pass

def HALSetNewDataSem(sem):
    pass

def HALInitialize(mode=0):
    pass

def HALNetworkCommunicationObserveUserProgramStarting():
    pass

def HALNetworkCommunicationObserveUserProgramDisabled():
    pass

def HALNetworkCommunicationObserveUserProgramAutonomous():
    pass

def HALNetworkCommunicationObserveUserProgramTeleop():
    pass

def HALNetworkCommunicationObserveUserProgramTest():
    pass

def HALReport(resource, instanceNumber, context=0, feature=None):
    pass


#############################################################################
# Accelerometer
#############################################################################

def setAccelerometerActive(active):
    pass

def setAccelerometerRange(range):
    pass

def getAccelerometerX():
    pass

def getAccelerometerY():
    pass

def getAccelerometerZ():
    pass


#############################################################################
# Analog
#############################################################################

def initializeAnalogOutputPort(port, status):
    pass

def setAnalogOutput(analog_port, voltage, status):
    pass

def getAnalogOutput(analog_port, status):
    pass

def checkAnalogOutputChannel(pin):
    pass

def initializeAnalogInputPort(port, status):
    pass

def checkAnalogModule(module):
    pass

def checkAnalogInputChannel(pin):
    pass

def setAnalogSampleRate(samples_per_second, status):
    pass

def getAnalogSampleRate(status):
    pass

def setAnalogAverageBits(analog_port, bits, status):
    pass

def getAnalogAverageBits(analog_port, status):
    pass

def setAnalogOversampleBits(analog_port, bits, status):
    pass

def getAnalogOversampleBits(analog_port, status):
    pass

def getAnalogValue(analog_port, status):
    pass

def getAnalogAverageValue(analog_port, status):
    pass

def getAnalogVoltsToValue(analog_port, voltage, status):
    pass

def getAnalogVoltage(analog_port, status):
    pass

def getAnalogAverageVoltage(analog_port, status):
    pass

def getAnalogLSBWeight(analog_port, status):
    pass

def getAnalogOffset(analog_port, status):
    pass

def isAccumulatorChannel(analog_port, status):
    pass

def initAccumulator(analog_port, status):
    pass

def resetAccumulator(analog_port, status):
    pass

def setAccumulatorCenter(analog_port, status):
    pass

def setAccumulatorDeadband(analog_port, deadband, status):
    pass

def getAccumulatorValue(analog_port, status):
    pass

def getAccumulatorCount(analog_port, status):
    pass

def getAccumulatorOutput(analog_port, status):
    pass

def initializeAnalogTrigger(port, status):
    pass

def cleanAnalogTrigger(analog_trigger, status):
    pass

def setAnalogTriggerLimitsRaw(analog_trigger, lower, upper, status):
    pass

def setAnalogTriggerLimitsVoltage(analog_trigger, lower, upper, status):
    pass

def setAnalogTriggerAveraged(analog_trigger, use_averaged_value, status):
    pass

def setAnalogTriggerFiltered(analog_trigger, use_filtered_value, status):
    pass

def getAnalogTriggerInWindow(analog_trigger, status):
    pass

def getAnalogTriggerTriggerState(analog_trigger, status):
    pass

def getAnalogTriggerOutput(analog_trigger, type, status):
    pass


#############################################################################
# Compressor
#############################################################################

def initializeCompressor(module):
    pass

def checkCompressorModule(module):
    pass

def getCompressor(pcm, status):
    pass

def setClosedLoopControl(pcm, value, status):
    pass

def getClosedLoopControl(pcm, status):
    pass

def getPressureSwitch(pcm, status):
    pass

def getCompressorCurrent(pcm, status):
    pass


#############################################################################
# Digital
#############################################################################

def initializeDigitalPort(port, status):
    pass

def checkPWMChannel(digital_port):
    pass

def checkRelayChannel(digital_port):
    pass

def setPWM(digital_port, value, status):
    pass

def allocatePWMChannel(digital_port, status):
    pass

def freePWMChannel(digital_port, status):
    pass

def getPWM(digital_port, status):
    pass

def latchPWMZero(digital_port, status):
    pass

def setPWMPeriodScale(digital_port, squelch_mask, status):
    pass

def allocatePWM(status):
    pass

def freePWM(pwm, status):
    pass

def setPWMRate(rate, status):
    pass

def setPWMDutyCycle(pwm, duty_cycle, status):
    pass

def setPWMOutputChannel(pwm, pin, status):
    pass

def setRelayForward(digital_port, on, status):
    pass

def setRelayReverse(digital_port, on, status):
    pass

def getRelayForward(digital_port, status):
    pass

def getRelayReverse(digital_port, status):
    pass

def allocateDIO(digital_port, input, status):
    pass

def freeDIO(digital_port, status):
    pass

def setDIO(digital_port, value, status):
    pass

def getDIO(digital_port, status):
    pass

def getDIODirection(digital_port, status):
    pass

def pulse(digital_port, pulse_length, status):
    pass

def isPulsing(digital_port, status):
    pass

def isAnyPulsing(status):
    pass

def initializeCounter(mode, status):
    pass

def freeCounter(counter, status):
    pass

def setCounterAverageSize(counter, size, status):
    pass

def setCounterUpSource(counter, pin, analog_trigger, status):
    pass

def setCounterUpSourceEdge(counter, rising_edge, falling_edge, status):
    pass

def clearCounterUpSource(counter, status):
    pass

def setCounterDownSource(counter, pin, analog_trigger, status):
    pass

def setCounterDownSourceEdge(counter, rising_edge, falling_edge, status):
    pass

def clearCounterDownSource(counter, status):
    pass

def setCounterUpDownMode(counter, status):
    pass

def setCounterExternalDirectionMode(counter, status):
    pass

def setCounterSemiPeriodMode(counter, high_semi_period, status):
    pass

def setCounterPulseLengthMode(counter, threshold, status):
    pass

def getCounterSamplesToAverage(counter, status):
    pass

def setCounterSamplesToAverage(counter, samples_to_average, status):
    pass

def resetCounter(counter, status):
    pass

def getCounter(counter, status):
    pass

def getCounterPeriod(counter, status):
    pass

def setCounterMaxPeriod(counter, max_period, status):
    pass

def setCounterUpdateWhenEmpty(counter, enabled, status):
    pass

def getCounterStopped(counter, status):
    pass

def getCounterDirection(counter, status):
    pass

def setCounterReverseDirection(counter, reverse_direction, status):
    pass

def initializeEncoder(port_a_module, port_a_pin, port_a_analog_trigger, port_b_module, port_b_pin, port_b_analog_trigger, reverse_direction, status):
    pass

def freeEncoder(encoder, status):
    pass

def resetEncoder(encoder, status):
    pass

def getEncoder(encoder, status):
    pass

def getEncoderPeriod(encoder, status):
    pass

def setEncoderMaxPeriod(encoder, max_period, status):
    pass

def getEncoderStopped(encoder, status):
    pass

def getEncoderDirection(encoder, status):
    pass

def setEncoderReverseDirection(encoder, reverse_direction, status):
    pass

def setEncoderSamplesToAverage(encoder, samples_to_average, status):
    pass

def getEncoderSamplesToAverage(encoder, status):
    pass

def getLoopTiming(status):
    pass

def spiInitialize(port, status):
    pass

def spiTransaction(port, data_to_send, data_received, size):
    pass

def spiWrite(port, data_to_send, send_size):
    pass

def spiRead(port, buffer, count):
    pass

def spiClose(port):
    pass

def spiSetSpeed(port, speed):
    pass

def spiSetOpts(port, msb_first, sample_on_trailing, clk_idle_high):
    pass

def spiSetChipSelectActiveHigh(port, status):
    pass

def spiSetChipSelectActiveLow(port, status):
    pass

def spiGetHandle(port):
    pass

def spiSetHandle(port, handle):
    pass

def spiGetSemaphore(port):
    pass

def spiSetSemaphore(port, semaphore):
    pass

def i2CInitialize(port, status):
    pass

def i2CTransaction(port, device_address, data_to_send, send_size, data_received, receive_size):
    pass

def i2CWrite(port, device_address, data_to_send, send_size):
    pass

def i2CRead(port, device_address, buffer, count):
    pass

def i2CClose(port):
    pass


#############################################################################
# Interrupts
#############################################################################

def initializeInterrupts(interrupt_index, watcher, status):
    pass

def cleanInterrupts(interrupt, status):
    pass

def waitForInterrupt(interrupt, timeout, ignorePrevious, status):
    pass

def enableInterrupts(interrupt, status):
    pass

def disableInterrupts(interrupt, status):
    pass

def readRisingTimestamp(interrupt, status):
    pass

def readFallingTimestamp(interrupt, status):
    pass

def requestInterrupts(interrupt, routing_module, routing_pin, routing_analog_trigger, status):
    pass

def attachInterruptHandler(interrupt, handler, param, status):
    pass

def setInterruptUpSourceEdge(interrupt, rising_edge, falling_edge, status):
    pass


#############################################################################
# Notifier
#############################################################################

def initializeNotifier(processQueue, status):
    pass

def cleanNotifier(notifier, status):
    pass

def updateNotifierAlarm(notifier, triggerTime, status):
    pass


#############################################################################
# PDP
#############################################################################

def getPDPTemperature(status):
    pass

def getPDPVoltage(status):
    pass

def getPDPChannelCurrent(channel, status):
    pass


#############################################################################
# Power
#############################################################################

def getVinVoltage(status):
    pass

def getVinCurrent(status):
    pass

def getUserVoltage6V(status):
    pass

def getUserCurrent6V(status):
    pass

def getUserVoltage5V(status):
    pass

def getUserCurrent5V(status):
    pass

def getUserVoltage3V3(status):
    pass

def getUserCurrent3V3(status):
    pass

def initializeSolenoidPort(port, status):
    pass

def checkSolenoidModule(module):
    pass


#############################################################################
# Solenoid
#############################################################################

def getSolenoid(solenoid_port, status):
    pass

def setSolenoid(solenoid_port, value, status):
    pass


#############################################################################
# Utilities
#############################################################################

HAL_NO_WAIT = 0
HAL_WAIT_FOREVER = -1

def delayTicks(ticks):
    pass

def delayMillis(ms):
    pass

def delaySeconds(s):
    pass

