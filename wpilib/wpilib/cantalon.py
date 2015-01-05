import hal
import weakref

from .motorsafety import MotorSafety
from .resource import Resource
from .timer import Timer

__all__ = ["CANTalon"]

def _freeCANTalon(handle):
    hal.TalonSRX_Destroy(handle)

class CANTalon(MotorSafety):
    """Talon SRX device as a CAN device

    The TALON SRX is designed to instrument all runtime signals periodically.
    The default periods are chosen to support 16 TALONs with 10ms update rate
    for control (throttle or setpoint).  However these can be overridden with
    :meth:`setStatusFrameRate`.

    Likewise most control signals are sent periodically using the
    fire-and-forget CAN API.

    Signals that are not available in an unsolicited fashion are the Close
    Loop gains.  For teams that have a single profile for their TALON close
    loop they can use either the webpage to configure their TALONs once or
    set the PIDF,Izone,CloseLoopRampRate,etc... once in the robot application.
    These parameters are saved to flash so once they are loaded in the TALON,
    they will persist through power cycles and mode changes.

    For teams that have one or two profiles to switch between, they can use
    the same strategy since there are two slots to choose from and the
    ProfileSlotSelect is periodically sent in the 10 ms control frame.

    For teams that require changing gains frequently, they can use the
    soliciting API to get and set those parameters.  Most likely they will
    only need to set them in a periodic fashion as a function of what motion
    the application is attempting.  If this API is used, be mindful of the CAN
    utilization reported in the driver station.

    Encoder position is measured in encoder edges.  Every edge is counted
    (similar to roboRIO 4X mode).  Analog position is 10 bits, meaning 1024
    ticks per rotation (0V => 3.3V).  Use :meth:`setFeedbackDevice` to select
    which sensor type you need.  Once you do that you can use
    :meth:`getSensorPosition` and :meth:`getSensorVelocity`.  These signals
    are updated on CANBus every 20ms (by default).  If a relative sensor is
    selected, you can zero (or change the current value) using
    :meth:`setSensorPosition`.

    Analog Input and quadrature position (and velocity) are also explicitly
    reported in :meth:`getEncPosition`, :meth:`getEncVelocity`,
    :meth:`getAnalogInPosition`, :meth:`getAnalogInRaw`,
    :meth:`getAnalogInVelocity`.
    These signals are available all the time, regardless of what sensor is
    selected at a rate of 100ms.  This allows easy instrumentation for "in the
    pits" checking of all sensors regardless of modeselect.  The 100ms rate is
    overridable for teams who want to acquire sensor data for processing, not
    just instrumentation.  Or just select the sensor using
    :meth:`setFeedbackDevice` to get it at 20ms.

    Velocity is in position ticks / 100ms.

    All output units are in respect to duty cycle (throttle) which is
    -1023(full reverse) to +1023 (full forward).  This includes demand (which
    specifies duty cycle when in duty cycle mode) and rampRamp, which is in
    throttle units per 10ms (if nonzero).

    When in (default) PercentVBus mode, set() and get() are automatically
    scaled to a -1.0 to +1.0 range to match other motor controllers.

    Pos and velocity close loops are calc'd as::

        err = target - posOrVel
        iErr += err
        if IZone != 0 and abs(err) > IZone:
            ClearIaccum()
        output = P * err + I * iErr + D * dErr + F * target
        dErr = err - lastErr

    P, I, and D gains are always positive. F can be negative.

    Motor direction can be reversed using :meth:`reverseOutput` if sensor
    and motor are out of phase.  Similarly feedback sensor can also be reversed
    (multiplied by -1) using :meth:`reverseSensor` if you prefer the sensor to
    be inverted.

    P gain is specified in throttle per error tick.  For example, a value of
    102 is ~9.9% (which is 102/1023) throttle per 1 ADC unit(10bit) or 1
    quadrature encoder edge depending on selected sensor.

    I gain is specified in throttle per integrated error. For example, a value
    of 10 equates to ~0.99% (which is 10/1023) for each accumulated ADC
    unit(10bit) or 1 quadrature encoder edge depending on selected sensor.
    Close loop and integral accumulator runs every 1ms.

    D gain is specified in throttle per derivative error. For example a value
    of 102 equates to ~9.9% (which is 102/1023) per change of 1 unit (ADC or
    encoder) per ms.

    I Zone is specified in the same units as sensor position (ADC units or
    quadrature edges).  If pos/vel error is outside of this value, the
    integrated error will auto-clear::

        if IZone != 0 and abs(err) > IZone:
            ClearIaccum()

    This is very useful in preventing integral windup and is highly
    recommended if using full PID to keep stability low.

    CloseLoopRampRate is in throttle units per 1ms.  Set to zero to disable
    ramping.  Works the same as RampThrottle but only is in effect when a
    close loop mode and profile slot is selected.
    """

    class ControlMode:
        PercentVbus = hal.TalonSRXConst.kMode_DutyCycle
        Position = hal.TalonSRXConst.kMode_PositionCloseLoop
        Speed = hal.TalonSRXConst.kMode_VelocityCloseLoop
        Current = hal.TalonSRXConst.kMode_CurrentCloseLoop
        Voltage = hal.TalonSRXConst.kMode_VoltCompen
        Follower = hal.TalonSRXConst.kMode_SlaveFollower
        Disabled = hal.TalonSRXConst.kMode_NoDrive

    class FeedbackDevice:
        QuadEncoder = hal.TalonSRXConst.kFeedbackDev_DigitalQuadEnc
        AnalogPot = hal.TalonSRXConst.kFeedbackDev_AnalogPot
        AnalogEncoder = hal.TalonSRXConst.kFeedbackDev_AnalogEncoder
        EncRising = hal.TalonSRXConst.kFeedbackDev_CountEveryRisingEdge
        EncFalling = hal.TalonSRXConst.kFeedbackDev_CountEveryFallingEdge

    class StatusFrameRate:
        """enumerated types for frame rate ms"""
        General = hal.TalonSRXConst.kStatusFrame_General
        Feedback = hal.TalonSRXConst.kStatusFrame_Feedback
        QuadEncoder = hal.TalonSRXConst.kStatusFrame_Encoder
        AnalogTempVbat = hal.TalonSRXConst.kStatusFrame_AnalogTempVbat

    kDelayForSolicitedSignals = 0.004

    def __init__(self, deviceNumber,
                 controlPeriodMs=hal.TalonSRXConst.kDefaultControlPeriodMs):
        MotorSafety.__init__(self)

        self.deviceNumber = deviceNumber
        # HAL bounds period to be within [1 ms,95 ms]
        self._handle = hal.TalonSRX_Create(deviceNumber, controlPeriodMs)
        self._handle_finalizer = weakref.finalize(self, _freeCANTalon,
                                                  self._handle)
        self.controlEnabled = True
        self.profile = 0
        self.setPoint = 0.0
        self.setProfile(self.profile)
        self._applyControlMode(self.ControlMode.PercentVbus)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

    @property
    def handle(self):
        if not self._handle_finalizer.alive:
            raise ValueError("operation on freed port")
        return self._handle

    def free(self):
        self._handle_finalizer()

    def pidWrite(self, output):
        if self.getControlMode() == self.ControlMode.PercentVbus:
            self.set(output)
        else:
            raise ValueError("PID only supported in PercentVbus mode")

    def set(self, outputValue, syncGroup=0):
        """
        Sets the appropriate output on the talon, depending on the mode.

        In PercentVbus, the output is between -1.0 and 1.0, with 0.0 as stopped.

        In Follower mode, the output is the integer device ID of the talon to
            duplicate.

        In Voltage mode, outputValue is in volts.

        In Current mode, outputValue is in amperes.

        In Speed mode, outputValue is in position change / 10ms.

        In Position mode, outputValue is in encoder ticks or an analog value,
            depending on the sensor.

        :param outputValue: The setpoint value, as described above.
        """
        if not self.controlEnabled:
            return
        self.setPoint = outputValue
        if self.controlMode == self.ControlMode.PercentVbus:
            if outputValue > 1:
                outputValue = 1
            elif outputValue < -1:
                outputValue = -1
            hal.TalonSRX_SetDemand(self.handle, int(1023*outputValue))
        elif self.controlMode == self.ControlMode.Follower:
            hal.TalonSRX_SetDemand(self.handle, int(outputValue))
        elif self.controlMode == self.ControlMode.Voltage:
            # Voltage is an 8.8 fixed point number.
            volts = int(outputValue * 256)
            hal.TalonSRX_SetDemand(self.handle, volts)
        elif self.controlMode == self.ControlMode.Speed:
            hal.TalonSRX_SetDemand(self.handle, int(outputValue))
        elif self.controlMode == self.ControlMode.Position:
            hal.TalonSRX_SetDemand(self.handle, int(outputValue))
        hal.TalonSRX_SetModeSelect(self.handle, self.controlMode)

    def reverseSensor(self, flip):
        """
        Flips the sign (multiplies by negative one) the sensor values going
        into the talon.

        This only affects position and velocity closed loop control. Allows for
          situations where you may have a sensor flipped and going in the wrong
          direction.

        :param flip: True if sensor input should be flipped; False if not.
        """
        hal.TalonSRX_SetRevFeedbackSensor(self.handle, 1 if flip else 0)

    def reverseOutput(self, flip):
        """
        Flips the sign (multiplies by negative one) the throttle values going
        into the motor on the talon in closed loop modes.

        :param flip: True if motor output should be flipped; False if not.
        """
        hal.TalonSRX_SetRevMotDuringCloseLoopEn(self.handle, 1 if flip else 0)

    def get(self):
        """
        Gets the current status of the Talon (usually a sensor value).

        In Current mode: returns output current.

        In Speed mode: returns current speed.

        In Position omde: returns current sensor position.

        In Throttle and Follower modes: returns current applied throttle.

        :returns: The current sensor value of the Talon.
        """
        if self.controlMode == self.ControlMode.Voltage:
            return self.getOutputVoltage()
        elif self.controlMode == self.ControlMode.Current:
            return self.getOutputCurrent()
        elif self.controlMode == self.ControlMode.Speed:
            return float(hal.TalonSRX_GetSensorVelocity(self.handle))
        elif self.controlMode == self.ControlMode.Position:
            return float(hal.TalonSRX_GetSensorPosition(self.handle))
        else: # PercentVbus
            return hal.TalonSRX_GetAppliedThrottle(self.handle) / 1023.0

    def getEncPosition(self):
        """
        Get the current encoder position, regardless of whether it is the
        current feedback device.

        :returns: The current position of the encoder.
        """
        return hal.TalonSRX_GetEncPosition(self.handle)

    def getEncVelocity(self):
        """
        Get the current encoder velocity, regardless of whether it is the
        current feedback device.

        :returns: The current speed of the encoder.
        """
        return hal.TalonSRX_GetEncVel(self.handle)

    def getNumberOfQuadIdxRises(self):
        """
        Get the number of of rising edges seen on the index pin.

        :returns: number of rising edges on idx pin.
        """
        return hal.TalonSRX_GetEncIndexRiseEvents(self.handle)

    def getPinStateQuadA(self):
        """
        :returns: IO level of QUADA pin.
        """
        return hal.TalonSRX_GetQuadApin(self.handle)

    def getPinStateQuadB(self):
        """
        :returns: IO level of QUADB pin.
        """
        return hal.TalonSRX_GetQuadBpin(self.handle)

    def getPinStateQuadIdx(self):
        """
        :returns: IO level of QUAD Index pin.
        """
        return hal.TalonSRX_GetQuadIdxpin(self.handle)

    def getAnalogInPosition(self):
        """
        Get the current analog in position, regardless of whether it is the
        current feedback device.

        :returns: The 24bit analog position.  The bottom ten bits is the ADC
            (0 - 1023) on the analog pin of the Talon. The upper 14 bits
            tracks the overflows and underflows (continuous sensor).
        """
        return hal.TalonSRX_GetAnalogInWithOv(self.handle)

    def getAnalogInRaw(self):
        """
        Get the current analog in position, regardless of whether it is the
        current feedback device.
        :returns: The ADC (0 - 1023) on analog pin of the Talon.
        """
        return self.getAnalogInPosition() & 0x3FF

    def getAnalogInVelocity(self):
        """
        Get the current encoder velocity, regardless of whether it is the
        current feedback device.

        :returns: The current speed of the analog in device.
        """
        return hal.TalonSRX_GetAnalogInVel(self.handle)

    def getClosedLoopError(self):
        """
        Get the current difference between the setpoint and the sensor value.

        :returns: The error, in whatever units are appropriate.
        """
        return hal.TalonSRX_GetCloseLoopErr(self.handle)

    def isFwdLimitSwitchClosed(self):
        """Returns True if limit switch is closed. False if open."""
        return hal.TalonSRX_GetLimitSwitchClosedFor(self.handle) == 0

    def isRevLimitSwitchClosed(self):
        """Returns True if limit switch is closed. False if open."""
        return hal.TalonSRX_GetLimitSwitchClosedRev(self.handle) == 0

    def getBrakeEnableDuringNeutral(self):
        """Returns True if break is enabled during neutral. False if coast."""
        return hal.TalonSRX_GetBrakeIsEnabled(self.handle) != 0

    def getTemp(self):
        """Returns temperature of Talon, in degrees Celsius."""
        return hal.TalonSRX_GetTemp(self.handle)

    def getSensorPosition(self):
        return hal.TalonSRX_GetSensorPosition(self.handle)

    def getSensorVelocity(self):
        return hal.TalonSRX_GetSensorVelocity(self.handle)

    def getOutputCurrent(self):
        """Returns the current going through the Talon, in Amperes."""
        return hal.TalonSRX_GetCurrent(self.handle)

    def getOutputVoltage(self):
        """
        :returns: The voltage being output by the Talon, in Volts.
        """
        return self.getBusVoltage() * hal.TalonSRX_GetAppliedThrottle(self.handle) / 1023.0

    def getBusVoltage(self):
        """
        :returns: The voltage at the battery terminals of the Talon, in Volts.
        """
        return hal.TalonSRX_GetBatteryV(self.handle)

    def getPosition(self):
        return hal.TalonSRX_GetSensorPosition(self.handle)

    def setPosition(self, pos):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eSensorPosition,
                              int(pos))

    def getSpeed(self):
        return hal.TalonSRX_GetSensorVelocity(self.handle)

    def getControlMode(self):
        return self.controlMode

    def _applyControlMode(self, controlMode):
        """
        Fixup the self.controlMode so set() serializes the correct demand value.
        Also fills the modeSelecet in the control frame to disabled.
        :param controlMode: Control mode to ultimately enter once user calls
            set().
        """
        self.controlMode = controlMode
        if controlMode == self.ControlMode.Disabled:
            self.controlEnabled = False
        # Disable until set() is called.
        hal.TalonSRX_SetModeSelect(self.handle, self.ControlMode.Disabled)

    def changeControlMode(self, controlMode):
        # if we already are in this mode, don't perform disable workaround
        if self.controlMode != controlMode:
            self._applyControlMode(controlMode)

    def setFeedbackDevice(self, device):
        hal.TalonSRX_SetFeedbackDeviceSelect(self.handle, device)

    def setStatusFrameRateMs(self, stateFrame, periodMs):
        """Change the periodMs of a TALON's status frame.  See StatusFrameRate
        enum for what's available."""
        hal.TalonSRX_SetStatusFrameRate(self.handle, stateFrame, periodMs)

    def enableControl(self):
        self.changeControlMode(self.controlMode)
        self.controlEnabled = True

    def disableControl(self):
        hal.TalonSRX_SetModeSelect(self.handle, self.ControlMode.Disabled)
        self.controlEnabled = False

    def isControlEnabled(self):
        return self.controlEnabled

    def _getParam(self, paramEnum):
        # Update the information that we have.
        hal.TalonSRX_RequestParam(self.handle, paramEnum)

        # Briefly wait for new values from the Talon.
        Timer.delay(self.kDelayForSolicitedSignals)

        return hal.TalonSRX_GetParamResponse(self.handle, paramEnum)

    def _getParamInt(self, paramEnum):
        # Update the information that we have.
        hal.TalonSRX_RequestParam(self.handle, paramEnum)

        # Briefly wait for new values from the Talon.
        Timer.delay(self.kDelayForSolicitedSignals)

        return hal.TalonSRX_GetParamResponseInt32(self.handle, paramEnum)

    def getP(self):
        """
        Get the current proportional constant.

        :returns: double proportional constant for current profile.
        """
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_P)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_P)

    def getI(self):
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_I)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_I)

    def getD(self):
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_D)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_D)

    def getF(self):
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_F)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_F)

    def getIZone(self):
        if self.profile == 0:
            return self._getParamInt(hal.TalonSRXParam.eProfileParamSlot0_IZone)
        else:
            return self._getParamInt(hal.TalonSRXParam.eProfileParamSlot1_IZone)

    def getCloseLoopRampRate(self):
        """
        Get the closed loop ramp rate for the current profile.

        Limits the rate at which the throttle will change.
        Only affects position and speed closed loop modes.

        :returns: rampRate Maximum change in voltage, in volts / sec.

        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            throttlePerMs = self._getParamInt(hal.TalonSRXParam.eProfileParamSlot0_CloseLoopRampRate)
        else:
            throttlePerMs = self._getParamInt(hal.TalonSRXParam.eProfileParamSlot1_CloseLoopRampRate)

        return throttlePerMs / 1023.0 * 12.0 * 1000.0

    def getFirmwareVersion(self):
        """
        :returns: The version of the firmware running on the Talon
        """
        return self._getParamInt(hal.TalonSRXParam.eFirmVers)

    def getIaccum(self):
        return self._getParamInt(hal.TalonSRXParam.ePidIaccum)

    def clearIaccum(self):
        """
        Clear the accumulator for I gain.
        """
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.ePidIaccum, 0)

    def setP(self, p):
        """
        Set the proportional value of the currently selected profile.

        :param p: Proportional constant for the currently selected PID profile.
        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_P, p)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_P, p)

    def setI(self, i):
        """
        Set the integration constant of the currently selected profile.

        :param i: Integration constant for the currently selected PID profile.
        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_I, i)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_I, i)

    def setD(self, d):
        """
        Set the derivative constant of the currently selected profile.

        :param d: Derivative constant for the currently selected PID profile.
        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_D, d)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_D, d)

    def setF(self, f):
        """
        Set the feedforward value of the currently selected profile.

        :param f: Feedforward constant for the currently selected PID profile.
        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_F, f)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_F, f)

    def setIZone(self, izone):
        """
        Set the integration zone of the current Closed Loop profile.

        Whenever the error is larger than the izone value, the accumulated
        integration error is cleared so that high errors aren't racked up when
        at high errors.

        An izone value of 0 means no difference from a standard PIDF loop.

        :param izone: Width of the integration zone.
        :see: #setProfile For selecting a certain profile.
        """
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_IZone, izone)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_IZone, izone)

    def setCloseLoopRampRate(self, rampRate):
        """
        Set the closed loop ramp rate for the current profile.

        Limits the rate at which the throttle will change.
        Only affects position and speed closed loop modes.

        :param rampRate: Maximum change in voltage, in volts / sec.
        :see: #setProfile For selecting a certain profile.
        """
        # CanTalonSRX takes units of Throttle (0 - 1023) / 1ms.
        rate = int(rampRate * 1023.0 / 12.0 / 1000.0)
        if self.profile == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_CloseLoopRampRate, rate)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_CloseLoopRampRate, rate)

    def setVoltageRampRate(self, rampRate):
        """
        Set the voltage ramp rate for the current profile.

        Limits the rate at which the throttle will change.
        Affects all modes.

        :param rampRate: Maximum change in voltage, in volts / sec.
        """
        # CanTalonSRX takes units of Throttle (0 - 1023) / 10ms.
        rate = int(rampRate * 1023.0 / 12.0 /100.0)
        hal.TalonSRX_SetRampThrottle(self.handle, rate)

    def setPID(self, p, i, d, f=0, izone=0, closeLoopRampRate=0,
               profile=None):
        """
        Sets control values for closed loop control.

        :param p: Proportional constant.
        :param i: Integration constant.
        :param d: Differential constant.
        :param f: Feedforward constant.
        :param izone: Integration zone -- prevents accumulation of integration
            error with large errors. Setting this to zero will ignore any
            izone stuff.
        :param closeLoopRampRate: Closed loop ramp rate. Maximum change in
            voltage, in volts / sec.
        :param profile: which profile to set the pid constants for. You can
            have two profiles, with values of 0 or 1, allowing you to keep a
            second set of values on hand in the talon. In order to switch
            profiles without recalling setPID, you must call setProfile().
        """
        if profile is not None:
            self.setProfile(profile)
        self.setP(p)
        self.setI(i)
        self.setD(d)
        self.setF(f)
        self.setIZone(izone)
        self.setCloseLoopRampRate(closeLoopRampRate)

    def getSetpoint(self):
        """
        :returns: The latest value set using set().
        """
        return self.setPoint

    def setProfile(self, profile):
        """
        Select which closed loop profile to use, and uses whatever PIDF gains
        and the such that are already there.
        """
        if profile not in (0, 1):
            raise ValueError("Talon PID profile must be 0 or 1.")
        self.profile = profile
        hal.TalonSRX_SetProfileSlotSelect(self.handle, self.profile)

    def stopMotor(self):
        """
        Common interface for stopping a motor.
        """
        self.disableControl()

    def disable(self):
        self.disableControl()

    def getDeviceID(self):
        return self.deviceNumber

    # TODO: Documentation for all these accessors/setters for misc. stuff.

    def setSensorPosition(self, pos):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eSensorPosition, pos)

    def setForwardSoftLimit(self, forwardLimit):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForThreshold, forwardLimit)

    def enableForwardSoftLimit(self, enable):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForEnable, 1 if enable else 0)

    def setReverseSoftLimit(self, reverseLimit):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevThreshold, reverseLimit)

    def enableReverseSoftLimit(self, enable):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevEnable, 1 if enable else 0)

    def clearStickyFaults(self):
        hal.TalonSRX_ClearStickyFaults(self.handle)

    def enableLimitSwitch(self, forward, reverse):
        mask = 4 + (2 if forward else 0) + (1 if reverse else 0)
        hal.TalonSRX_SetOverrideLimitSwitchEn(self.handle, mask)

    def configFwdLimitSwitchNormallyOpen(self, normallyOpen):
        """
        Configure the fwd limit switch to be normally open or normally closed.
        Talon will disable momentarilly if the Talon's current setting
        is dissimilar to the caller's requested setting.

        Since Talon saves setting to flash this should only affect
        a given Talon initially during robot install.

        :param normallyOpen: True for normally open. False for normally closed.
        """
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eOnBoot_LimitSwitch_Forward_NormallyClosed, 0 if normallyOpen else 1)

    def configRevLimitSwitchNormallyOpen(self, normallyOpen):
        """
        * Configure the rev limit switch to be normally open or normally closed.
        * Talon will disable momentarilly if the Talon's current setting
        * is dissimilar to the caller's requested setting.
        *
        * Since Talon saves setting to flash this should only affect
        * a given Talon initially during robot install.
        *
        * @param normallyOpen true for normally open.  false for normally closed.
        """
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eOnBoot_LimitSwitch_Reverse_NormallyClosed, 0 if normallyOpen else 1)

    def enableBrakeMode(self, brake):
        hal.TalonSRX_SetOverrideBrakeType(self.handle, 2 if brake else 1)

    def getFaultOverTemp(self):
        return hal.TalonSRX_GetFault_OverTemp(self.handle)

    def getFaultUnderVoltage(self):
        return hal.TalonSRX_GetFault_UnderVoltage(self.handle)

    def getFaultForLim(self):
        return hal.TalonSRX_GetFault_ForLim(self.handle)

    def getFaultRevLim(self):
        return hal.TalonSRX_GetFault_RevLim(self.handle)

    def getFaultHardwareFailure(self):
        return hal.TalonSRX_GetFault_HardwareFailure(self.handle)

    def getFaultForSoftLim(self):
        return hal.TalonSRX_GetFault_ForSoftLim(self.handle)

    def getFaultRevSoftLim(self):
        return hal.TalonSRX_GetFault_RevSoftLim(self.handle)

    def getStickyFaultOverTemp(self):
        return hal.TalonSRX_GetStckyFault_OverTemp(self.handle)

    def getStickyFaultUnderVoltage(self):
        return hal.TalonSRX_GetStckyFault_UnderVoltage(self.handle)

    def getStickyFaultForLim(self):
        return hal.TalonSRX_GetStckyFault_ForLim(self.handle)

    def getStickyFaultRevLim(self):
        return hal.TalonSRX_GetStckyFault_RevLim(self.handle)

    def getStickyFaultForSoftLim(self):
        return hal.TalonSRX_GetStckyFault_ForSoftLim(self.handle)

    def getStickyFaultRevSoftLim(self):
        return hal.TalonSRX_GetStckyFault_RevSoftLim(self.handle)

    def getDescription(self):
        return "CANTalon ID %d" % self.deviceNumber
