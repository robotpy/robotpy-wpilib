#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2014. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
from hal import frccan
import struct
import warnings
import weakref

from .livewindowsendable import LiveWindowSendable
from .motorsafety import MotorSafety
from .resource import Resource
from .timer import Timer

from . import _canjaguar as _cj

__all__ = ["CANJaguar"]

def _packPercentage(value):
    if value < -1.0:
        value = -1.0
    if value > 1.0:
        value = 1.0
    return [x for x in struct.pack("<h", int(value * 32767.0))]

def _packFXP8_8(value):
    return [x for x in struct.pack("<h", int(value * 256.0))]

def _packFXP16_16(value):
    return [x for x in struct.pack("<i", int(value * 65536.0))]

def _packINT16(value):
    return [x for x in struct.pack("<h", int(value))]

def _packINT32(value):
    return [x for x in struct.pack("<i", int(value))]

def _unpackPercentage(buffer):
    return struct.unpack("<h", bytes(buffer[:2]))[0] / 32767.0

def _unpackFXP8_8(buffer):
    return struct.unpack("<h", bytes(buffer[:2]))[0] / 256.0

def _unpackFXP16_16(buffer):
    return struct.unpack("<i", bytes(buffer[:4]))[0] / 65536.0

def _unpackINT16(buffer):
    return struct.unpack("<h", bytes(buffer[:2]))[0]

def _unpackINT32(buffer):
    return struct.unpack("<i", bytes(buffer[:4]))[0]

def _FXP8_EQ(a, b):
    """Compare floats for equality as fixed point numbers"""
    return int(a * 256.0) == int(b * 256.0)

def _FXP16_EQ(a, b):
    """Compare floats for equality as fixed point numbers"""
    return int(a * 65536.0) == int(b * 65536.0)

def _sendMessageHelper(messageID, data, period):
    if (CANJaguar.kFullMessageIDMask & messageID) in CANJaguar.kTrustedMessages:
        # Make sure the data will still fit after adjusting for the token.
        if data is not None and len(data) > CANJaguar.kMaxMessageDataSize - 2:
            raise RuntimeError("CAN message has too much data.")

        trustedData = [0, 0] # token placeholder
        if data is not None:
            trustedData.extend(data)
        frccan.CANSessionMux_sendMessage(messageID, trustedData, period)
    else:
        frccan.CANSessionMux_sendMessage(messageID, data, period)

def _freeJaguar(deviceNumber, controlMode):
    # Cancel periodic messages to the Jaguar, effectively disabling it.
    # Disable periodic setpoints

    CANJaguar.allocated.free(deviceNumber-1)

    if controlMode == CANJaguar.ControlMode.PercentVbus:
        messageID = deviceNumber | _cj.LM_API_VOLT_T_SET
    elif controlMode == CANJaguar.ControlMode.Speed:
        messageID = deviceNumber | _cj.LM_API_SPD_T_SET
    elif controlMode == CANJaguar.ControlMode.Position:
        messageID = deviceNumber | _cj.LM_API_POS_T_SET
    elif controlMode == CANJaguar.ControlMode.Current:
        messageID = deviceNumber | _cj.LM_API_ICTRL_T_SET
    elif controlMode == CANJaguar.ControlMode.Voltage:
        messageID = deviceNumber | _cj.LM_API_VCOMP_T_SET
    else:
        return

    frccan.CANSessionMux_sendMessage(messageID, None,
                                     frccan.CAN_SEND_PERIOD_STOP_REPEATING)

    data = _packFXP8_8(CANJaguar.kApproxBusVoltage)
    _sendMessageHelper(_cj.LM_API_CFG_MAX_VOUT | deviceNumber, data, frccan.CAN_SEND_PERIOD_NO_REPEAT)

class CANJaguar(LiveWindowSendable, MotorSafety):
    """Texas Instruments Jaguar Speed Controller as a CAN device."""

    kMaxMessageDataSize = 8

    # The internal PID control loop in the Jaguar runs at 1kHz.
    kControllerRate = 1000
    kApproxBusVoltage = 12.0

    kReceiveStatusAttempts = 50

    allocated = Resource(63)

    kFullMessageIDMask = \
            _cj.CAN_MSGID_API_M | _cj.CAN_MSGID_MFR_M | _cj.CAN_MSGID_DTYPE_M
    kSendMessagePeriod = 20

    kTrustedMessages = set([
            _cj.LM_API_VOLT_T_EN, _cj.LM_API_VOLT_T_SET, _cj.LM_API_SPD_T_EN,
            _cj.LM_API_SPD_T_SET, _cj.LM_API_VCOMP_T_EN, _cj.LM_API_VCOMP_T_SET,
            _cj.LM_API_POS_T_EN, _cj.LM_API_POS_T_SET, _cj.LM_API_ICTRL_T_EN,
            _cj.LM_API_ICTRL_T_SET])

    class Mode:
        """Control Mode."""
        
        #: Sets an encoder as the speed reference only.
        kEncoder = 0
        
        #: Sets a quadrature encoder as the position and speed reference.
        kQuadEncoder = 1
        
        #: Sets a potentiometer as the position reference only.
        kPotentiometer = 2

    class ControlMode:
        """Determines how the Jaguar is controlled, used internally."""
        PercentVbus = 0
        Current = 1
        Speed = 2
        Position = 3
        Voltage = 4

    kCurrentFault = 1
    kTemperatureFault = 2
    kBusVoltageFault = 4
    kGateDriverFault = 8

    # Limit switch masks
    kForwardLimit = 1
    kReverseLimit = 2

    class NeutralMode:
        """Determines how the Jaguar behaves when sending a zero signal."""
        
        #: Use the NeutralMode that is set by the jumper wire on the CAN device
        Jumper = 0
        
        #: Stop the motor's rotation by applying a force.
        Brake = 1
        
        #: Do not attempt to stop the motor. Instead allow it to coast
        #: to a stop without applying resistance.
        Coast = 2

    class LimitMode:
        """Determines which sensor to use for position reference.
        Limit switches will always be used to limit the rotation. This can
        not be disabled.
        """
        
        #: Disables the soft position limits and only uses
        #: the limit switches to limit rotation.  See `getForwardLimitOK`
        #: and `getReverseLimitOK`.
        SwitchInputsOnly = 0
        
        #: Enables the soft position limits on the Jaguar.
        #: These will be used in addition to the limit switches. This does
        #: not disable the behavior of the limit switch input.
        #: See `configSoftPositionLimits`.
        SoftPositionLimits = 1

    def __init__(self, deviceNumber):
        """Constructor for the CANJaguar device.
        
        By default the device is configured in Percent mode.
        The control mode can be changed by calling one of the control modes.

        :param deviceNumber: The address of the Jaguar on the CAN bus.
        """
        MotorSafety.__init__(self)

        try:
            CANJaguar.allocated.allocate(self, deviceNumber-1)
        except IndexError as e:
            raise IndexError("CANJaguar device %d in use (increment index by one)" % deviceNumber) from e

        self.deviceNumber = deviceNumber
        self.value = 0.0

        # Parameters/configuration
        self.controlMode = CANJaguar.ControlMode.PercentVbus
        self.speedReference = _cj.LM_REF_NONE
        self.positionReference = _cj.LM_REF_NONE
        self.p = 0.0
        self.i = 0.0
        self.d = 0.0
        self.neutralMode = CANJaguar.NeutralMode.Jumper
        self.encoderCodesPerRev = 0
        self.potentiometerTurns = 0
        self.limitMode = CANJaguar.LimitMode.SwitchInputsOnly
        self.forwardLimit = 0.0
        self.reverseLimit = 0.0
        self.maxOutputVoltage = CANJaguar.kApproxBusVoltage
        self.voltageRampRate = 0.0
        self.faultTime = 0.0

        # Which parameters have been verified since they were last set?
        self.controlModeVerified = True
        self.speedRefVerified = True
        self.posRefVerified = True
        self.pVerified = True
        self.iVerified = True
        self.dVerified = True
        self.neutralModeVerified = True
        self.encoderCodesPerRevVerified = True
        self.potentiometerTurnsVerified = True
        self.forwardLimitVerified = True
        self.reverseLimitVerified = True
        self.limitModeVerified = True
        self.maxOutputVoltageVerified = True
        self.voltageRampRateVerified = True
        self.faultTimeVerified = True

        # Status data
        self.busVoltage = 0.0
        self.outputVoltage = 0.0
        self.outputCurrent = 0.0
        self.temperature = 0.0
        self.position = 0.0
        self.speed = 0.0
        self.limits = 0
        self.faults = 0
        self.firmwareVersion = 0
        self.hardwareVersion = 0

        # Which periodic status messages have we received at least once?
        self.receivedStatusMessage0 = False
        self.receivedStatusMessage1 = False
        self.receivedStatusMessage2 = False

        self.controlEnabled = True

        receivedFirmwareVersion = False

        # Request firmware and hardware version only once
        self.requestMessage(frccan.CAN_IS_FRAME_REMOTE |
                            _cj.CAN_MSGID_API_FIRMVER)
        self.requestMessage(_cj.LM_API_HWVER)

        # Establish finalizer
        self._canjaguar_finalizer = weakref.finalize(self, _freeJaguar,
                                                     self.deviceNumber,
                                                     self.controlMode)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

        # Wait until we've gotten all of the status data at least once.
        for i in range(CANJaguar.kReceiveStatusAttempts):
            Timer.delay(0.001)

            self.setupPeriodicStatus()
            self.updatePeriodicStatus()

            if not receivedFirmwareVersion:
                try:
                    data = self.getMessage(_cj.CAN_MSGID_API_FIRMVER,
                                           _cj.CAN_MSGID_FULL_M)
                    self.firmwareVersion = _unpackINT32(data)
                    receivedFirmwareVersion = True
                except frccan.CANMessageNotFound:
                    pass

            if (self.receivedStatusMessage0 and
                self.receivedStatusMessage1 and
                self.receivedStatusMessage2 and
                receivedFirmwareVersion):
                break
        else:
            raise frccan.CANMessageNotFound("message not found")

        try:
            data = self.getMessage(_cj.LM_API_HWVER, _cj.CAN_MSGID_FULL_M)
            self.hardwareVersion = data[0]
        except frccan.CANError:
            # Not all Jaguar firmware reports a hardware version.
            self.hardwareVersion = 0

        # 3330 was the first shipping RDK firmware version for the Jaguar
        if self.firmwareVersion >= 3330 or self.firmwareVersion < 108:
            from .driverstation import DriverStation
            if self.firmwareVersion < 3330:
                DriverStation.reportError("Jag %d firmware %d is too old (must be at least version 108 of the FIRST approved firmware)" % (self.deviceNumber, self.firmwareVersion), False)
            else:
                DriverStation.reportError("Jag %d firmware %d is not FIRST approved (must be at least version 108 of the FIRST approved firmware)" % (self.deviceNumber, self.firmwareVersion), False)

    def free(self):
        """
        Cancel periodic messages to the Jaguar, effectively disabling it.
        No other methods should be called after this is called.
        """
        self._canjaguar_finalizer()

    def getDeviceNumber(self):
        """:returns: The CAN ID passed in the constructor
        """
        return self.deviceNumber

    def get(self):
        """Get the recently set outputValue set point.

        The scale and the units depend on the mode the Jaguar is in.
        
        - In percentVbus mode, the outputValue is from -1.0 to 1.0 (same as
          PWM Jaguar).
        - In voltage mode, the outputValue is in volts.
        - In current mode, the outputValue is in amps.
        - In speed mode, the outputValue is in rotations/minute.
        - In position mode, the outputValue is in rotations.

        :returns: The most recently set outputValue set point.
        """
        return self.value

    def set(self, outputValue, syncGroup=0):
        """Sets the output set-point value.

        The scale and the units depend on the mode the Jaguar is in.
        
        - In percentVbus Mode, the outputValue is from -1.0 to 1.0 (same as
          PWM Jaguar).
        - In voltage Mode, the outputValue is in volts.
        - In current Mode, the outputValue is in amps.
        - In speed mode, the outputValue is in rotations/minute.
        - In position Mode, the outputValue is in rotations.

        :param outputValue: The set-point to sent to the motor controller.
        :param syncGroup: The update group to add this set() to, pending
            UpdateSyncGroup().  If 0 (default), update immediately.
        """
        if self.controlEnabled:
            if self.controlMode == self.ControlMode.PercentVbus:
                messageID = _cj.LM_API_VOLT_T_SET
                data = _packPercentage(outputValue)
            elif self.controlMode == self.ControlMode.Speed:
                messageID = _cj.LM_API_SPD_T_SET
                data = _packFXP16_16(outputValue)
            elif self.controlMode == self.ControlMode.Position:
                messageID = _cj.LM_API_POS_T_SET
                data = _packFXP16_16(outputValue)
            elif self.controlMode == self.ControlMode.Current:
                messageID = _cj.LM_API_ICTRL_T_SET
                data = _packFXP8_8(outputValue)
            elif self.controlMode == self.ControlMode.Voltage:
                messageID = _cj.LM_API_VCOMP_T_SET
                data = _packFXP8_8(outputValue)
            else:
                return

            if syncGroup != 0:
                data.append(syncGroup)

            self.sendMessage(messageID, data, self.kSendMessagePeriod)

            self.feed()

        self.value = outputValue

        self.verify()

    def verify(self):
        """Check all unverified params and make sure they're equal to their
        local cached versions. If a value isn't available, it gets requested.
        If a value doesn't match up, it gets set again.
        """
        # If the Jaguar lost power, everything should be considered unverified
        try:
            data = self.getMessage(_cj.LM_API_STATUS_POWER,
                                   _cj.CAN_MSGID_FULL_M)
            if data[0] != 0: # power cycled
                # Clear the power cycled bit
                data[0] = 1
                self.sendMessage(_cj.LM_API_STATUS_POWER, data[:1])

                # Mark everything as unverified
                self.controlModeVerified = False
                self.speedRefVerified = False
                self.posRefVerified = False
                self.neutralModeVerified = False
                self.encoderCodesPerRevVerified = False
                self.potentiometerTurnsVerified = False
                self.forwardLimitVerified = False
                self.reverseLimitVerified = False
                self.limitModeVerified = False
                self.maxOutputVoltageVerified = False
                self.faultTimeVerified = False

                if (self.controlMode == self.ControlMode.PercentVbus or
                    self.controlMode == self.ControlMode.Voltage):
                    self.voltageRampRateVerified = False
                else:
                    self.pVerified = False
                    self.iVerified = False
                    self.dVerified = False

                # Verify periodic status messages again
                self.receivedStatusMessage0 = False
                self.receivedStatusMessage1 = False
                self.receivedStatusMessage2 = False

                # Remove any old values from netcomms. Otherwise, parameters
                # are incorrectly marked as verified based on stale messages.
                messages = [
                    _cj.LM_API_SPD_REF, _cj.LM_API_POS_REF,
                    _cj.LM_API_SPD_PC, _cj.LM_API_POS_PC,
                    _cj.LM_API_ICTRL_PC, _cj.LM_API_SPD_IC,
                    _cj.LM_API_POS_IC, _cj.LM_API_ICTRL_IC,
                    _cj.LM_API_SPD_DC, _cj.LM_API_POS_DC,
                    _cj.LM_API_ICTRL_DC, _cj.LM_API_CFG_ENC_LINES,
                    _cj.LM_API_CFG_POT_TURNS, _cj.LM_API_CFG_BRAKE_COAST,
                    _cj.LM_API_CFG_LIMIT_MODE, _cj.LM_API_CFG_LIMIT_REV,
                    _cj.LM_API_CFG_MAX_VOUT, _cj.LM_API_VOLT_SET_RAMP,
                    _cj.LM_API_VCOMP_COMP_RAMP, _cj.LM_API_CFG_FAULT_TIME,
                    _cj.LM_API_CFG_LIMIT_FWD]

                for message in messages:
                    try:
                        data = self.getMessage(message, _cj.CAN_MSGID_FULL_M)
                    except frccan.CANMessageNotFound:
                        pass
        except frccan.CANMessageNotFound:
            self.requestMessage(_cj.LM_API_STATUS_POWER)

        # Verify that any recently set parameters are correct
        if not self.controlModeVerified and self.controlEnabled:
            try:
                data = self.getMessage(_cj.LM_API_STATUS_CMODE,
                                       _cj.CAN_MSGID_FULL_M)
                mode = data[0]
                if self.controlMode == mode:
                    self.controlModeVerified = True
                else:
                    # Enable control again to resend the control mode
                    self.enableControl()
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_STATUS_CMODE)

        if not self.speedRefVerified:
            try:
                data = self.getMessage(_cj.LM_API_SPD_REF, _cj.CAN_MSGID_FULL_M)
                speedRef = data[0]
                if self.speedReference == speedRef:
                    self.speedRefVerified = True
                else:
                    # It's wrong - set it again
                    self.setSpeedReference(self.speedReference)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_SPD_REF)

        if not self.posRefVerified:
            try:
                data = self.getMessage(_cj.LM_API_POS_REF, _cj.CAN_MSGID_FULL_M)
                posRef = data[0]
                if self.positionReference == posRef:
                    self.posRefVerified = True
                else:
                    # It's wrong - set it again
                    self.setPositionReference(self.positionReference)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_POS_REF)

        if not self.pVerified:
            message = 0
            if self.controlMode == self.ControlMode.Speed:
                message = _cj.LM_API_SPD_PC
            elif self.controlMode == self.ControlMode.Position:
                message = _cj.LM_API_POS_PC
            elif self.controlMode == self.ControlMode.Current:
                message = _cj.LM_API_ICTRL_PC

            if message != 0:
                try:
                    data = self.getMessage(message, _cj.CAN_MSGID_FULL_M)
                    p = _unpackFXP16_16(data)
                    if _FXP16_EQ(self.p, p):
                        self.pVerified = True
                    else:
                        # It's wrong - set it again
                        self.setP(self.p)
                except frccan.CANMessageNotFound:
                    # Verification is needed but not available - request it again.
                    self.requestMessage(message)

        if not self.iVerified:
            message = 0
            if self.controlMode == self.ControlMode.Speed:
                message = _cj.LM_API_SPD_IC
            elif self.controlMode == self.ControlMode.Position:
                message = _cj.LM_API_POS_IC
            elif self.controlMode == self.ControlMode.Current:
                message = _cj.LM_API_ICTRL_IC

            if message != 0:
                try:
                    data = self.getMessage(message, _cj.CAN_MSGID_FULL_M)
                    i = _unpackFXP16_16(data)
                    if _FXP16_EQ(self.i, i):
                        self.iVerified = True
                    else:
                        # It's wrong - set it again
                        self.setI(self.i)
                except frccan.CANMessageNotFound:
                    # Verification is needed but not available - request it again.
                    self.requestMessage(message)

        if not self.dVerified:
            message = 0
            if self.controlMode == self.ControlMode.Speed:
                message = _cj.LM_API_SPD_DC
            elif self.controlMode == self.ControlMode.Position:
                message = _cj.LM_API_POS_DC
            elif self.controlMode == self.ControlMode.Current:
                message = _cj.LM_API_ICTRL_DC

            if message != 0:
                try:
                    data = self.getMessage(message, _cj.CAN_MSGID_FULL_M)
                    d = _unpackFXP16_16(data)
                    if _FXP16_EQ(self.d, d):
                        self.dVerified = True
                    else:
                        # It's wrong - set it again
                        self.setD(self.d)
                except frccan.CANMessageNotFound:
                    # Verification is needed but not available - request it again.
                    self.requestMessage(message)

        if not self.neutralModeVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_BRAKE_COAST,
                                       _cj.CAN_MSGID_FULL_M)
                mode = data[0]
                if mode == self.neutralMode:
                    self.neutralModeVerified = True
                else:
                    #It's wrong - set it again
                    self.configNeutralMode(self.neutralMode)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_BRAKE_COAST)

        if not self.encoderCodesPerRevVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_ENC_LINES,
                                _cj.CAN_MSGID_FULL_M)
                codes = _unpackINT16(data)
                if codes == self.encoderCodesPerRev:
                    self.encoderCodesPerRevVerified = True
                else:
                    #It's wrong - set it again
                    self.configEncoderCodesPerRev(self.encoderCodesPerRev)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_ENC_LINES)

        if not self.potentiometerTurnsVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_POT_TURNS,
                                       _cj.CAN_MSGID_FULL_M)
                turns = _unpackINT16(data)
                if turns == self.potentiometerTurns:
                    self.potentiometerTurnsVerified = True
                else:
                    #It's wrong - set it again
                    self.configPotentiometerTurns(self.potentiometerTurns)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_POT_TURNS)

        if not self.limitModeVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_LIMIT_MODE,
                                       _cj.CAN_MSGID_FULL_M)
                mode = data[0]
                if mode == self.limitMode:
                    self.limitModeVerified = True
                else:
                    #It's wrong - set it again
                    self.configLimitMode(self.limitMode)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_LIMIT_MODE)

        if not self.forwardLimitVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_LIMIT_FWD,
                                       _cj.CAN_MSGID_FULL_M)
                limit = _unpackFXP16_16(data)
                if _FXP16_EQ(limit, self.forwardLimit):
                    self.forwardLimitVerified = True
                else:
                    #It's wrong - set it again
                    self.configForwardLimit(self.forwardLimit)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_LIMIT_FWD)

        if not self.reverseLimitVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_LIMIT_REV,
                                       _cj.CAN_MSGID_FULL_M)
                limit = _unpackFXP16_16(data)
                if _FXP16_EQ(limit, self.reverseLimit):
                    self.reverseLimitVerified = True
                else:
                    #It's wrong - set it again
                    self.configReverseLimit(self.reverseLimit)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_LIMIT_REV)

        if not self.maxOutputVoltageVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_MAX_VOUT,
                                       _cj.CAN_MSGID_FULL_M)
                voltage = _unpackFXP8_8(data)
                # The returned max output voltage is sometimes slightly higher
                # or lower than what was sent.  This should not trigger
                # resending the message.
                if abs(voltage - self.maxOutputVoltage) < 0.1:
                    self.maxOutputVoltageVerified = True
                else:
                    # It's wrong - set it again
                    self.configMaxOutputVoltage(self.maxOutputVoltage)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_MAX_VOUT)

        if not self.voltageRampRateVerified:
            if self.controlMode == CANJaguar.ControlMode.PercentVbus:
                try:
                    data = self.getMessage(_cj.LM_API_VOLT_SET_RAMP,
                                           _cj.CAN_MSGID_FULL_M)
                    rate = _unpackPercentage(data)
                    if _FXP16_EQ(rate, self.voltageRampRate):
                        self.voltageRampRateVerified = True
                    else:
                        # It's wrong - set it again
                        self.setVoltageRampRate(self.voltageRampRate)
                except frccan.CANMessageNotFound:
                    # Verification is needed but not available - request it again.
                    self.requestMessage(_cj.LM_API_VOLT_SET_RAMP)
            elif self.controlMode == CANJaguar.ControlMode.Voltage:
                try:
                    data = self.getMessage(_cj.LM_API_VCOMP_COMP_RAMP,
                                           _cj.CAN_MSGID_FULL_M)
                    rate = _unpackFXP8_8(data)
                    if _FXP8_EQ(rate, self.voltageRampRate):
                        self.voltageRampRateVerified = True
                    else:
                        # It's wrong - set it again
                        self.setVoltageRampRate(self.voltageRampRate)
                except frccan.CANMessageNotFound:
                    # Verification is needed but not available - request it again.
                    self.requestMessage(_cj.LM_API_VCOMP_COMP_RAMP)

        if not self.faultTimeVerified:
            try:
                data = self.getMessage(_cj.LM_API_CFG_FAULT_TIME,
                                       _cj.CAN_MSGID_FULL_M)
                faultTime = _unpackINT16(data)
                if int(self.faultTime * 1000.0) == faultTime:
                    self.faultTimeVerified = True
                else:
                    #It's wrong - set it again
                    self.configFaultTime(self.faultTime)
            except frccan.CANMessageNotFound:
                # Verification is needed but not available - request it again.
                self.requestMessage(_cj.LM_API_CFG_FAULT_TIME)

        if (not self.receivedStatusMessage0 or
            not self.receivedStatusMessage1 or
            not self.receivedStatusMessage2):
            # If the periodic status messages haven't been verified as
            # received, request periodic status messages again and attempt
            # to unpack any available ones.
            self.setupPeriodicStatus()
            self.getTemperature()
            self.getPosition()
            self.getFaults()

    def disable(self):
        """Common interface for disabling a motor.

        .. deprecated :: 2015
            Use :func:`disableControl` instead.
        """
        warnings.warn("use disableControl instead", DeprecationWarning)
        self.disableControl()

    # PIDOutput interface
    def pidWrite(self, output):
        if self.controlMode == self.ControlMode.PercentVbus:
            self.set(output)
        else:
            raise ValueError("PID only supported in PercentVbus mode")

    def setSpeedReference(self, reference):
        """Set the reference source device for speed controller mode.

        Choose encoder as the source of speed feedback when in speed control
        mode.

        :param reference: Specify a speed reference.
        """
        self.sendMessage(_cj.LM_API_SPD_REF, [reference])
        self.speedReference = reference
        self.speedRefVerified = False

    def setPositionReference(self, reference):
        """Set the reference source device for position controller mode.

        Choose between using and encoder and using a potentiometer
        as the source of position feedback when in position control mode.

        :param reference: Specify a position reference.
        """
        self.sendMessage(_cj.LM_API_POS_REF, [reference])
        self.positionReference = reference
        self.posRefVerified = False

    def setP(self, p):
        """Set the P constant for the closed loop modes.

        :param p: The proportional gain of the Jaguar's PID controller.
        """
        data = _packFXP16_16(p)

        if self.controlMode == self.ControlMode.Speed:
            self.sendMessage(_cj.LM_API_SPD_PC, data)
        elif self.controlMode == self.ControlMode.Position:
            self.sendMessage(_cj.LM_API_POS_PC, data)
        elif self.controlMode == self.ControlMode.Current:
            self.sendMessage(_cj.LM_API_ICTRL_PC, data)
        else:
            raise ValueError("PID constants only apply in Speed, Position, and Current mode")

        self.p = p
        self.pVerified = False

    def setI(self, i):
        """Set the I constant for the closed loop modes.

        :param i: The integral gain of the Jaguar's PID controller.
        """
        data = _packFXP16_16(i)

        if self.controlMode == self.ControlMode.Speed:
            self.sendMessage(_cj.LM_API_SPD_IC, data)
        elif self.controlMode == self.ControlMode.Position:
            self.sendMessage(_cj.LM_API_POS_IC, data)
        elif self.controlMode == self.ControlMode.Current:
            self.sendMessage(_cj.LM_API_ICTRL_IC, data)
        else:
            raise ValueError("PID constants only apply in Speed, Position, and Current mode")

        self.i = i
        self.iVerified = False

    def setD(self, d):
        """Set the D constant for the closed loop modes.

        :param d: The derivative gain of the Jaguar's PID controller.
        """
        data = _packFXP16_16(d)

        if self.controlMode == self.ControlMode.Speed:
            self.sendMessage(_cj.LM_API_SPD_DC, data)
        elif self.controlMode == self.ControlMode.Position:
            self.sendMessage(_cj.LM_API_POS_DC, data)
        elif self.controlMode == self.ControlMode.Current:
            self.sendMessage(_cj.LM_API_ICTRL_DC, data)
        else:
            raise ValueError("PID constants only apply in Speed, Position, and Current mode")

        self.d = d
        self.dVerified = False

    def setPID(self, p, i, d):
        """Set the P, I, and D constants for the closed loop modes.

        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.setP(p)
        self.setI(i)
        self.setD(d)

    def getP(self):
        """Get the Proportional gain of the controller.

        :returns: The proportional gain.
        """
        if (self.controlMode == self.ControlMode.PercentVbus or
            self.controlMode == self.ControlMode.Voltage):
            raise ValueError("PID does not apply in Percent or Voltage control modes")
        return self.p

    def getI(self):
        """Get the Integral gain of the controller.

        :returns: The integral gain.
        """
        if (self.controlMode == self.ControlMode.PercentVbus or
            self.controlMode == self.ControlMode.Voltage):
            raise ValueError("PID does not apply in Percent or Voltage control modes")
        return self.i

    def getD(self):
        """Get the Derivative gain of the controller.

        :returns: The derivative gain.
        """
        if (self.controlMode == self.ControlMode.PercentVbus or
            self.controlMode == self.ControlMode.Voltage):
            raise ValueError("PID does not apply in Percent or Voltage control modes")
        return self.d

    def enableControl(self, encoderInitialPosition=0.0):
        """Enable the closed loop controller.

        Start actually controlling the output based on the feedback.
        If starting a position controller with an encoder reference,
        use the encoderInitialPosition parameter to initialize the
        encoder state.

        :param encoderInitialPosition: Encoder position to set if position
            with encoder reference (default of 0.0).  Ignored otherwise.
        """
        if self.controlMode == self.ControlMode.PercentVbus:
            self.sendMessage(_cj.LM_API_VOLT_T_EN, None)
        elif self.controlMode == self.ControlMode.Speed:
            self.sendMessage(_cj.LM_API_SPD_T_EN, None)
        elif self.controlMode == self.ControlMode.Position:
            data = _packFXP16_16(encoderInitialPosition)
            self.sendMessage(_cj.LM_API_POS_T_EN, data)
        elif self.controlMode == self.ControlMode.Current:
            self.sendMessage(_cj.LM_API_ICTRL_T_EN, None)
        elif self.controlMode == self.ControlMode.Voltage:
            self.sendMessage(_cj.LM_API_VCOMP_T_EN, None)

        self.controlEnabled = True

    def disableControl(self):
        """Disable the closed loop controller.

        Stop driving the output based on the feedback.
        """
        # Disable all control modes.
        self.sendMessage(_cj.LM_API_VOLT_DIS, None)
        self.sendMessage(_cj.LM_API_SPD_DIS, None)
        self.sendMessage(_cj.LM_API_POS_DIS, None)
        self.sendMessage(_cj.LM_API_ICTRL_DIS, None)
        self.sendMessage(_cj.LM_API_VCOMP_DIS, None)

        # Stop all periodic setpoints
        self.sendMessage(_cj.LM_API_VOLT_T_SET, None,
                         frccan.CAN_SEND_PERIOD_STOP_REPEATING)
        self.sendMessage(_cj.LM_API_SPD_T_SET, None,
                         frccan.CAN_SEND_PERIOD_STOP_REPEATING)
        self.sendMessage(_cj.LM_API_POS_T_SET, None,
                         frccan.CAN_SEND_PERIOD_STOP_REPEATING)
        self.sendMessage(_cj.LM_API_ICTRL_T_SET, None,
                         frccan.CAN_SEND_PERIOD_STOP_REPEATING)
        self.sendMessage(_cj.LM_API_VCOMP_T_SET, None,
                         frccan.CAN_SEND_PERIOD_STOP_REPEATING)

        self.controlEnabled = False

    def setPercentMode(self):
        """Enable controlling the motor voltage as a percentage of the bus
        voltage without any position or speed feedback.

        After calling this you must call :func:`enableControl` to enable
        the device.
        """
        self.changeControlMode(self.ControlMode.PercentVbus)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_NONE)

    def setPercentModeEncoder(self, codesPerRev):
        """Enable controlling the motor voltage as a percentage of the bus
        voltage, and enable speed sensing from a non-quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        """
        self.changeControlMode(self.ControlMode.PercentVbus)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)

    def setPercentModeQuadEncoder(self, codesPerRev):
        """Enable controlling the motor voltage as a percentage of the bus
        voltage, and enable position and speed sensing from a quadrature
        encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param tag: The constant {@link CANJaguar#kQuadEncoder}
        :param codesPerRev: The counts per revolution on the encoder
        """
        self.changeControlMode(self.ControlMode.PercentVbus)
        self.setPositionReference(_cj.LM_REF_ENCODER)
        self.setSpeedReference(_cj.LM_REF_QUAD_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)

    def setPercentModePotentiometer(self):
        """Enable controlling the motor voltage as a percentage of the bus
        voltage, and enable position sensing from a potentiometer and no
        speed feedback.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param tag: The constant {@link CANJaguar#kPotentiometer}
        """
        self.changeControlMode(self.ControlMode.PercentVbus)
        self.setPositionReference(_cj.LM_REF_POT)
        self.setSpeedReference(_cj.LM_REF_NONE)
        self.configPotentiometerTurns(1)

    def setCurrentModePID(self, p, i, d):
        """Enable controlling the motor current with a PID loop.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Current)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_NONE)
        self.setPID(p, i, d)

    def setCurrentModeEncoder(self, codesPerRev, p, i, d):
        """Enable controlling the motor current with a PID loop, and enable
        speed sensing from a non-quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Current)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_NONE)
        self.configEncoderCodesPerRev(codesPerRev)
        self.setPID(p, i, d)

    def setCurrentModeQuadEncoder(self, codesPerRev, p, i, d):
        """Enable controlling the motor current with a PID loop, and enable
        speed and position sensing from a quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Current)
        self.setPositionReference(_cj.LM_REF_ENCODER)
        self.setSpeedReference(_cj.LM_REF_QUAD_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)
        self.setPID(p, i, d)

    def setCurrentModePotentiometer(self, p, i, d):
        """Enable controlling the motor current with a PID loop, and enable
        position sensing from a potentiometer.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Current)
        self.setPositionReference(_cj.LM_REF_POT)
        self.setSpeedReference(_cj.LM_REF_NONE)
        self.configPotentiometerTurns(1)
        self.setPID(p, i, d)

    def setSpeedModeEncoder(self, codesPerRev, p, i, d):
        """Enable controlling the speed with a feedback loop from a
        non-quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Speed)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)
        self.setPID(p, i, d)

    def setSpeedModeQuadEncoder(self, codesPerRev, p, i, d):
        """Enable controlling the speed with a feedback loop from a
        quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Speed)
        self.setPositionReference(_cj.LM_REF_ENCODER)
        self.setSpeedReference(_cj.LM_REF_QUAD_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)
        self.setPID(p, i, d)

    def setPositionModeQuadEncoder(self, codesPerRev, p, i, d):
        """Enable controlling the position with a feedback loop using an
        encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Position)
        self.setPositionReference(_cj.LM_REF_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)
        self.setPID(p, i, d)

    def setPositionModePotentiometer(self, p, i, d):
        """Enable controlling the position with a feedback loop using a
        potentiometer.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param p: The proportional gain of the Jaguar's PID controller.
        :param i: The integral gain of the Jaguar's PID controller.
        :param d: The differential gain of the Jaguar's PID controller.
        """
        self.changeControlMode(self.ControlMode.Position)
        self.setPositionReference(_cj.LM_REF_POT)
        self.configPotentiometerTurns(1)
        self.setPID(p, i, d)

    def setVoltageMode(self):
        """Enable controlling the motor voltage without any position or speed
        feedback.

        After calling this you must call :func:`enableControl` to enable
        the device.
        """
        self.changeControlMode(self.ControlMode.Voltage)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_NONE)

    def setVoltageModeEncoder(self, codesPerRev):
        """Enable controlling the motor voltage with speed feedback from a
        non-quadrature encoder and no position feedback.<br>

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param codesPerRev: The counts per revolution on the encoder
        """
        self.changeControlMode(self.ControlMode.Voltage)
        self.setPositionReference(_cj.LM_REF_NONE)
        self.setSpeedReference(_cj.LM_REF_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)

    def setVoltageModeQuadEncoder(self, codesPerRev):
        """Enable controlling the motor voltage with position and speed
        feedback from a quadrature encoder.

        After calling this you must call :func:`enableControl` to enable
        the device.

        :param tag: The constant {@link CANJaguar#kQuadEncoder}
        :param codesPerRev: The counts per revolution on the encoder
        """
        self.changeControlMode(self.ControlMode.Voltage)
        self.setPositionReference(_cj.LM_REF_ENCODER)
        self.setSpeedReference(_cj.LM_REF_QUAD_ENCODER)
        self.configEncoderCodesPerRev(codesPerRev)

    def setVoltageModePotentiometer(self):
        """Enable controlling the motor voltage with position feedback from a
        potentiometer and no speed feedback.

        After calling this you must call :func:`enableControl` to enable
        the device.
        """
        self.changeControlMode(self.ControlMode.Voltage)
        self.setPositionReference(_cj.LM_REF_POT)
        self.setSpeedReference(_cj.LM_REF_NONE)
        self.configPotentiometerTurns(1)

    def changeControlMode(self, controlMode):
        """Used internally.  In order to set the control mode see the methods
        listed below.

        Change the control mode of this Jaguar object.

        After changing modes, configure any PID constants or other settings
        needed and then EnableControl() to actually change the mode on the
        Jaguar.

        :param controlMode: The new mode.
        """
        # Disable the previous mode
        self.disableControl()

        # Update the local mode
        self.controlMode = controlMode
        self.controlModeVerified = False

        # Update the finalizer
        self._canjaguar_finalizer.detach()
        self._canjaguar_finalizer = weakref.finalize(self, _freeJaguar,
                                                     self.deviceNumber,
                                                     self.controlMode)

    def getControlMode(self):
        """Get the active control mode from the Jaguar.

        Ask the Jagaur what mode it is in.

        :return ControlMode: that the Jag is in.
        """
        return self.controlMode

    def getBusVoltage(self):
        """Get the voltage at the battery input terminals of the Jaguar.

        :returns: The bus voltage in Volts.
        """
        self.updatePeriodicStatus()
        return self.busVoltage

    def getOutputVoltage(self):
        """Get the voltage being output from the motor terminals of the Jaguar.

        :returns: The output voltage in Volts.
        """
        self.updatePeriodicStatus()
        return self.outputVoltage

    def getOutputCurrent(self):
        """Get the current through the motor terminals of the Jaguar.

        :returns: The output current in Amps.
        """
        self.updatePeriodicStatus()
        return self.outputCurrent

    def getTemperature(self):
        """Get the internal temperature of the Jaguar.

        :returns: The temperature of the Jaguar in degrees Celsius.
        """
        self.updatePeriodicStatus()
        return self.temperature

    def getPosition(self):
        """Get the position of the encoder or potentiometer.

        :returns: The position of the motor in rotations based on the
            configured feedback. See :func:`configPotentiometerTurns` and
            :func:`configEncoderCodesPerRev`.
        """
        self.updatePeriodicStatus()
        return self.position

    def getSpeed(self):
        """Get the speed of the encoder.

        :returns: The speed of the motor in RPM based on the configured
            feedback.
        """
        self.updatePeriodicStatus()
        return self.speed

    def getForwardLimitOK(self):
        """Get the status of the forward limit switch.

        :returns: True if the motor is allowed to turn in the forward direction.
        """
        self.updatePeriodicStatus()
        return (self.limits & self.kForwardLimit) != 0

    def getReverseLimitOK(self):
        """Get the status of the reverse limit switch.

        :returns: True if the motor is allowed to turn in the reverse direction.
        """
        self.updatePeriodicStatus()
        return (self.limits & self.kReverseLimit) != 0

    def getFaults(self):
        """Get the status of any faults the Jaguar has detected.

        :returns: A bit-mask of faults defined by the "Faults" constants.
        
                  - `kCurrentFault`
                  - `kBusVoltageFault`
                  - `kTemperatureFault`
                  - `GateDriverFault`
        """
        self.updatePeriodicStatus()
        return self.faults

    def setVoltageRampRate(self, rampRate):
        """Set the maximum voltage change rate.

        When in PercentVbus or Voltage output mode, the rate at which the
        voltage changes can be limited to reduce current spikes.  set this
        to 0.0 to disable rate limiting.

        :param rampRate: The maximum rate of voltage change in Percent
            Voltage mode in V/s.
        """
        if self.controlMode == self.ControlMode.PercentVbus:
            data = _packPercentage(rampRate / (self.maxOutputVoltage *
                                               self.kControllerRate))
            message = _cj.LM_API_VOLT_SET_RAMP
        elif self.controlMode == self.ControlMode.Voltage:
            data = _packFXP8_8(rampRate / self.kControllerRate)
            message = _cj.LM_API_VCOMP_COMP_RAMP
        else:
            raise ValueError("Voltage ramp rate only applies in Percentage and Voltage modes")

        self.sendMessage(message, data)

    def getFirmwareVersion(self):
        """Get the version of the firmware running on the Jaguar.

        :returns: The firmware version.  0 if the device did not respond.
        """
        return self.firmwareVersion

    def getHardwareVersion(self):
        """Get the version of the Jaguar hardware.

        :returns: The hardware version. 1: Jaguar,  2: Black Jaguar
        """
        return self.hardwareVersion

    def configNeutralMode(self, mode):
        """Configure what the controller does to the H-Bridge when neutral
        (not driving the output).

        This allows you to override the jumper configuration for brake or coast.

        :param mode: Select to use the jumper setting or to override it to
            coast or brake (see `NeutralMode`).
        """
        self.sendMessage(_cj.LM_API_CFG_BRAKE_COAST, [mode])
        self.neutralMode = mode
        self.neutralModeVerified = False

    def configEncoderCodesPerRev(self, codesPerRev):
        """Configure how many codes per revolution are generated by your
        encoder.

        :param codesPerRev: The number of counts per revolution in 1X mode.
        """
        data = _packINT16(codesPerRev)
        self.sendMessage(_cj.LM_API_CFG_ENC_LINES, data)
        self.encoderCodesPerRev = codesPerRev
        self.encoderCodesPerRevVerified = False

    def configPotentiometerTurns(self, turns):
        """Configure the number of turns on the potentiometer.

        There is no special support for continuous turn potentiometers.
        Only integer numbers of turns are supported.

        :param turns: The number of turns of the potentiometer
        """
        data = _packINT16(turns)
        self.sendMessage(_cj.LM_API_CFG_POT_TURNS, data)
        self.potentiometerTurns = turns
        self.potentiometerTurnsVerified = False

    def configSoftPositionLimits(self, forwardLimitPosition,
                                 reverseLimitPosition):
        """Configure Soft Position Limits when in Position Controller mode.

        When controlling position, you can add additional limits on top of
        the limit switch inputs that are based on the position feedback.
        If the position limit is reached or the switch is opened, that
        direction will be disabled.

        :param forwardLimitPosition: The position that, if exceeded, will
            disable the forward direction.
        :param reverseLimitPosition: The position that, if exceeded, will
            disable the reverse direction.
        """
        self.configLimitMode(self.LimitMode.SoftPositionLimits)
        self.configForwardLimit(forwardLimitPosition)
        self.configReverseLimit(reverseLimitPosition)

    def disableSoftPositionLimits(self):
        """Disable Soft Position Limits if previously enabled.<br>

        Soft Position Limits are disabled by default.
        """
        self.configLimitMode(self.LimitMode.SwitchInputsOnly)

    def configLimitMode(self, mode):
        """Set the limit mode for position control mode.<br>

        Use :func:`configSoftPositionLimits` or
        :func:`disableSoftPositionLimits` to set this automatically.

        :param mode: The `LimitMode` to use to limit the rotation of the device.
        """
        self.sendMessage(_cj.LM_API_CFG_LIMIT_MODE, [mode])

    def configForwardLimit(self, forwardLimitPosition):
        """Set the position that, if exceeded, will disable the forward
        direction.

        Use :func:`configSoftPositionLimits` to set this and the
        `LimitMode` automatically.

        :param forwardLimitPosition: The position that, if exceeded, will
            disable the forward direction.
        """
        data = _packFXP16_16(forwardLimitPosition)
        data.append(1)
        self.sendMessage(_cj.LM_API_CFG_LIMIT_FWD, data)

        self.forwardLimit = forwardLimitPosition
        self.forwardLimitVerified = False

    def configReverseLimit(self, reverseLimitPosition):
        """Set the position that, if exceeded, will disable the reverse
        direction.

        Use :func:`configSoftPositionLimits` to set this and the
        `LimitMode` automatically.

        :param reverseLimitPosition: The position that, if exceeded, will
            disable the reverse direction.
        """
        data = _packFXP16_16(reverseLimitPosition)
        data.append(1)
        self.sendMessage(_cj.LM_API_CFG_LIMIT_REV, data)

        self.reverseLimit = reverseLimitPosition
        self.reverseLimitVerified = False

    def configMaxOutputVoltage(self, voltage):
        """Configure the maximum voltage that the Jaguar will ever output.

        This can be used to limit the maximum output voltage in all modes so
        that motors which cannot withstand full bus voltage can be used safely.

        :param voltage: The maximum voltage output by the Jaguar.
        """
        data = _packFXP8_8(voltage)
        self.sendMessage(_cj.LM_API_CFG_MAX_VOUT, data)

        self.maxOutputVoltage = voltage
        self.maxOutputVoltageVerified = False

    def configFaultTime(self, faultTime):
        """Configure how long the Jaguar waits in the case of a fault before
        resuming operation.

        Faults include over temerature, over current, and bus under voltage.
        The default is 3.0 seconds, but can be reduced to as low as 0.5
        seconds.

        :param faultTime: The time to wait before resuming operation, in
            seconds.
        """
        if faultTime < 0.5:
            faultTime = 0.5
        elif faultTime > 3.0:
            faultTime = 3.0

        data = _packINT16(int(faultTime * 1000.0))
        self.sendMessage(_cj.LM_API_CFG_FAULT_TIME, data)

        self.faultTime = faultTime
        self.faultTimeVerified = False

    def sendMessage(self, messageID, data,
                    period=frccan.CAN_SEND_PERIOD_NO_REPEAT):
        """Send a message to the Jaguar.

        :param messageID: The messageID to be used on the CAN bus (device
            number is added internally)
        :param data: The up to 8 bytes of data to be sent with the message
        :param period: If positive, tell Network Communications to send the
            message every "period" milliseconds.
        """
        _sendMessageHelper(messageID | self.deviceNumber, data, period)

    def requestMessage(self, messageID,
                       period=frccan.CAN_SEND_PERIOD_NO_REPEAT):
        """Request a message from the Jaguar, but don't wait for it to arrive.

        :param messageID: The message to request
        :param periodic: If positive, tell Network Communications to request
            the message every "period" milliseconds.
        """
        _sendMessageHelper(messageID | self.deviceNumber, None, period)

    def getMessage(self, messageID, messageMask):
        """Get a previously requested message.

        Jaguar always generates a message with the same message ID when
        replying.

        :param messageID: The messageID to read from the CAN bus (device
            number is added internally)
        :returns: The up to 8 bytes of data that was received with the message
        """
        messageID |= self.deviceNumber
        messageID &= _cj.CAN_MSGID_FULL_M

        # Get the data.
        messageID, data, timeStamp = \
                frccan.CANSessionMux_receiveMessage(messageID, messageMask)

        return data

    def setupPeriodicStatus(self):
        """Enables periodic status updates from the Jaguar
        """
        # Message 0 returns bus voltage, output voltage, output current, and
        # temperature.
        kMessage0Data = [
            _cj.LM_PSTAT_VOLTBUS_B0, _cj.LM_PSTAT_VOLTBUS_B1,
            _cj.LM_PSTAT_VOLTOUT_B0, _cj.LM_PSTAT_VOLTOUT_B1,
            _cj.LM_PSTAT_CURRENT_B0, _cj.LM_PSTAT_CURRENT_B1,
            _cj.LM_PSTAT_TEMP_B0, _cj.LM_PSTAT_TEMP_B1]

        # Message 1 returns position and speed
        kMessage1Data = [
            _cj.LM_PSTAT_POS_B0, _cj.LM_PSTAT_POS_B1,
            _cj.LM_PSTAT_POS_B2, _cj.LM_PSTAT_POS_B3,
            _cj.LM_PSTAT_SPD_B0, _cj.LM_PSTAT_SPD_B1,
            _cj.LM_PSTAT_SPD_B2, _cj.LM_PSTAT_SPD_B3]

        # Message 2 returns limits and faults
        kMessage2Data = [
            _cj.LM_PSTAT_LIMIT_CLR,
            _cj.LM_PSTAT_FAULT,
            _cj.LM_PSTAT_END,
            0, 0, 0, 0, 0]

        data = _packINT16(int(self.kSendMessagePeriod))
        self.sendMessage(_cj.LM_API_PSTAT_PER_EN_S0, data)
        self.sendMessage(_cj.LM_API_PSTAT_PER_EN_S1, data)
        self.sendMessage(_cj.LM_API_PSTAT_PER_EN_S2, data)

        self.sendMessage(_cj.LM_API_PSTAT_CFG_S0, kMessage0Data)
        self.sendMessage(_cj.LM_API_PSTAT_CFG_S1, kMessage1Data)
        self.sendMessage(_cj.LM_API_PSTAT_CFG_S2, kMessage2Data)

    def updatePeriodicStatus(self):
        """Check for new periodic status updates and unpack them into local
        variables.
        """
        # Check if a new bus voltage/output voltage/current/temperature message
        # has arrived and unpack the values into the cached member variables
        try:
            data = self.getMessage(_cj.LM_API_PSTAT_DATA_S0,
                                   _cj.CAN_MSGID_FULL_M)

            self.busVoltage    = _unpackFXP8_8(data[0:2])
            self.outputVoltage = _unpackPercentage(data[2:4]) * self.busVoltage
            self.outputCurrent = _unpackFXP8_8(data[4:6])
            self.temperature   = _unpackFXP8_8(data[6:8])

            self.receivedStatusMessage0 = True
        except frccan.CANMessageNotFound:
            pass

        # Check if a new position/speed message has arrived and do the same
        try:
            data = self.getMessage(_cj.LM_API_PSTAT_DATA_S1,
                                   _cj.CAN_MSGID_FULL_M)

            self.position = _unpackFXP16_16(data[0:4])
            self.speed    = _unpackFXP16_16(data[4:8])

            self.receivedStatusMessage1 = True
        except frccan.CANMessageNotFound:
            pass

        # Check if a new limits/faults message has arrived and do the same
        try:
            data = self.getMessage(_cj.LM_API_PSTAT_DATA_S2,
                                   _cj.CAN_MSGID_FULL_M)
            self.limits = data[0]
            self.faults = data[1]

            self.receivedStatusMessage2 = True
        except frccan.CANMessageNotFound:
            pass

    @staticmethod
    def updateSyncGroup(syncGroup):
        """Update all the motors that have pending sets in the syncGroup.

        :param syncGroup: A bitmask of groups to generate synchronous output.
        """
        _sendMessageHelper(_cj.CAN_MSGID_API_SYNC, [syncGroup],
                           frccan.CAN_SEND_PERIOD_NO_REPEAT)

    def getDescription(self):
        return "CANJaguar ID %d" % self.deviceNumber

    def getDeviceID(self):
        return self.deviceNumber

    def stopMotor(self):
        """Common interface for stopping a motor.
        """
        self.disableControl()

    # Live Window code, only does anything if live window is activated.

    def getSmartDashboardType(self):
        return "Speed Controller"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putNumber("Value", self.get())

    def valueChanged(self, itable, key, value, bln):
        self.set(float(value))

    def startLiveWindowMode(self):
        self.set(0)  # Stop for safety
        super(CANJaguar, self).startLiveWindowMode()

    def stopLiveWindowMode(self):
        super(CANJaguar, self).stopLiveWindowMode()
        self.set(0)  # Stop for safety
