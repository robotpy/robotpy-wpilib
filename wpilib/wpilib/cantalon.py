# validated: 2016-02-17 DS 952ebb1 athena/java/edu/wpi/first/wpilibj/CANTalon.java
import hal
import weakref

from .interfaces import PIDSource
from .livewindow import LiveWindow
from .livewindowsendable import LiveWindowSendable
from .motorsafety import MotorSafety
from .resource import Resource
from .timer import Timer

__all__ = ["CANTalon"]

def _freeCANTalon(handle):
    hal.TalonSRX_Destroy(handle)

class CANTalon(LiveWindowSendable, MotorSafety):
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
    
    If calling application has used the config routines to configure the
    selected feedback sensor, then all positions are measured in floating point
    precision rotations.  All sensor velocities are specified in floating point
    precision RPM.
    
    .. seealso: :meth:`configPotentiometerTurns`, :meth:`configEncoderCodesPerRev`
    
    HOWEVER, if calling application has not called the config routine for
    selected feedback sensor, then all getters/setters for position/velocity use
    the native engineering units of the Talon SRX firm (just like in 2015).
    Signals explained below.

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
    
    #: Number of adc engineering units per 0 to 3.3V sweep.
    #: This is necessary for scaling Analog Position in rotations/RPM.
    kNativeAdcUnitsPerRotation = 1024
    
    #: Number of pulse width engineering units per full rotation.
    #: This is necessary for scaling Pulse Width Decoded Position in rotations/RPM.
    kNativePwdUnitsPerRotation = 4096.0
    
    #: Number of minutes per 100ms unit.  Useful for scaling velocities
    #: measured by Talon's 100ms timebase to rotations per minute.
    kMinutesPer100msUnit = 1.0/600.0
    
    PIDSourceType = PIDSource.PIDSourceType

    class ControlMode:
        PercentVbus = hal.TalonSRXConst.kMode_DutyCycle
        Position = hal.TalonSRXConst.kMode_PositionCloseLoop
        Speed = hal.TalonSRXConst.kMode_VelocityCloseLoop
        Current = hal.TalonSRXConst.kMode_CurrentCloseLoop
        Voltage = hal.TalonSRXConst.kMode_VoltCompen
        Follower = hal.TalonSRXConst.kMode_SlaveFollower
        MotionProfile = hal.TalonSRXConst.kMode_MotionProfile
        Disabled = hal.TalonSRXConst.kMode_NoDrive

    class FeedbackDevice:
        QuadEncoder = hal.TalonSRXConst.kFeedbackDev_DigitalQuadEnc
        AnalogPot = hal.TalonSRXConst.kFeedbackDev_AnalogPot
        AnalogEncoder = hal.TalonSRXConst.kFeedbackDev_AnalogEncoder
        EncRising = hal.TalonSRXConst.kFeedbackDev_CountEveryRisingEdge
        EncFalling = hal.TalonSRXConst.kFeedbackDev_CountEveryFallingEdge
        CtreMagEncoder_Relative = hal.TalonSRXConst.kFeedbackDev_CtreMagEncoder_Relative
        CtreMagEncoder_Absolute = hal.TalonSRXConst.kFeedbackDev_CtreMagEncoder_Absolute
        PulseWidth = hal.TalonSRXConst.kFeedbackDev_PosIsPulseWidth
        
    class FeedbackDeviceStatus:
        Unknown = hal.TalonSRXConst.kFeedbackDevStatus_Unknown
        Present = hal.TalonSRXConst.kFeedbackDevStatus_Present
        NotPresent = hal.TalonSRXConst.kFeedbackDevStatus_NotPresent

    class StatusFrameRate:
        """enumerated types for frame rate ms"""
        General = hal.TalonSRXConst.kStatusFrame_General
        Feedback = hal.TalonSRXConst.kStatusFrame_Feedback
        QuadEncoder = hal.TalonSRXConst.kStatusFrame_Encoder
        AnalogTempVbat = hal.TalonSRXConst.kStatusFrame_AnalogTempVbat
        PulseWidth = hal.TalonSRXConst.kStatusFrame_PulseWidth
        
    class SetValueMotionProfile:
        """Enumerated types for Motion Control Set Values.
        
        When in Motion Profile control mode, these constants are paseed
        into set() to manipulate the motion profile executer.
        
        When changing modes, be sure to read the value back using :meth:`.getMotionProfileStatus`
        to ensure changes in output take effect before performing buffering actions.
        
        Disable will signal Talon to put motor output into neutral drive.
        
        Talon will stop processing motion profile points.  This means the buffer is
        effectively disconnected from the executer, allowing the robot to gracefully
        clear and push new traj points.  isUnderrun will get cleared.
        The active trajectory is also cleared.
        
        Enable will signal Talon to pop a trajectory point from it's buffer and process it.
        If the active trajectory is empty, Talon will shift in the next point.
        If the active traj is empty, and so is the buffer, the motor drive is neutral and
        isUnderrun is set.  When active traj times out, and buffer has at least one point,
        Talon shifts in next one, and isUnderrun is cleared.  When active traj times out,
        and buffer is empty, Talon keeps processing active traj and sets IsUnderrun.
        
        Hold will signal Talon keep processing the active trajectory indefinitely.
        If the active traj is cleared, Talon will neutral motor drive.  Otherwise
        Talon will keep processing the active traj but it will not shift in
        points from the buffer.  This means the buffer is  effectively disconnected
        from the executer, allowing the robot to gracefully clear and push
        new traj points.
        isUnderrun is set if active traj is empty, otherwise it is cleared.
        isLast signal is also cleared.
        
        Typical workflow:
        
        - set(Disable),
        - Confirm Disable takes effect,
        - clear buffer and push buffer points,
        - set(Enable) when enough points have been pushed to ensure no underruns,
        - wait for MP to finish or decide abort,
        - If MP finished gracefully set(Hold) to hold position servo and disconnect buffer,
        - If MP is being aborted set(Disable) to neutral the motor and disconnect buffer,
        - Confirm mode takes effect,
        - clear buffer and push buffer points, and rinse-repeat.
        """
        
        Disable = hal.TalonSRXConst.kMotionProfile_Disable
        Enable = hal.TalonSRXConst.kMotionProfile_Enable
        Hold = hal.TalonSRXConst.kMotionProfile_Hold
        
    class TrajectoryPoint:
        '''This is a data transfer object'''
        
        #: (double) the position to servo to
        position = 0
        
        #: (double) The velocity to feed-forward
        velocity = 0
        
        #: (int) Time in milliseconds to process this point.
        #: Value should be between 1ms and 255ms.  If value is zero
        #: then Talon will default to 1ms.  If value exceeds 255ms API will cap it.
        timeDurMs = 0
        
        #: (int) Which slot to get PIDF gains.
        #: PID is used for position servo.
        #: F is used as the Kv constant for velocity feed-forward.
        #: Typically this is hardcoded to the a particular slot, but you are free
        #: gain schedule if need be.
        profileSlotSelect = 0
        
        #: Set to true to only perform the velocity feed-forward and not perform
        #: position servo.  This is useful when learning how the position servo
        #: changes the motor response.  The same could be accomplish by clearing the
        #: PID gains, however this is synchronous the streaming, and doesn't require restoing
        #: gains when finished.
        #: 
        #: Additionaly setting this basically gives you direct control of the motor output
        #: since motor output = targetVelocity X Kv, where Kv is our Fgain.
        #: This means you can also scheduling straight-throttle curves without relying on
        #: a sensor.    
        velocityOnly = False
        
        #: (bool) Set to true to signal Talon that this is the final point, so do not
        #: attempt to pop another trajectory point from out of the Talon buffer.
        #: Instead continue processing this way point.  Typically the velocity
        #: member variable should be zero so that the motor doesn't spin indefinitely.
        isLastPoint = False

        #: (bool) Set to true to signal Talon to zero the selected sensor.
        #: When generating MPs, one simple method is to make the first target position zero,
        #: and the final target position the target distance from the current position.
        #: Then when you fire the MP, the current position gets set to zero.
        #: If this is the intent, you can set zeroPos on the first trajectory point.
        #: 
        #: Otherwise you can leave this false for all points, and offset the positions
        #: of all trajectory points so they are correct.
        zeroPos = False
  
    class MotionProfileStatus:
        '''This is simply a data transfer object'''
        
        _flags = 0
        
        #: (int) The available empty slots in the trajectory buffer.
        #: 
        #: The robot API holds a "top buffer" of trajectory points, so your applicaion
        #: can dump several points at once.  The API will then stream them into the Talon's
        #: low-level buffer, allowing the Talon to act on them.
        topBufferRem = 0
    
        #: (int) The number of points in the top trajectory buffer.
        topBufferCnt = 0
        
        #: (int) The number of points in the low level Talon buffer.
        btmBufferCnt = 0
    
        @property
        def hasUnderrun(self):
            """(bool) Set if isUnderrun ever gets set.
            Only is cleared by :meth:`clearMotionProfileHasUnderrun` to ensure
            robot logic can react or instrument it.
            
            .. seealso:: :meth:`clearMotionProfileHasUnderrun`"""
            return (self._flags & hal.TalonSRXConst.kMotionProfileFlag_HasUnderrun) != 0
    
        @property
        def isUnderrun(self):
            """(bool) This is set if Talon needs to shift a point from its buffer into
            the active trajectory point however the buffer is empty. This gets cleared
            automatically when is resolved."""
            return (self._flags & hal.TalonSRXConst.kMotionProfileFlag_IsUnderrun) != 0
        
        @property
        def activePointValid(self):
            """(bool) True if the active trajectory point has not empty, false otherwise.
            The members in activePoint are only valid if this signal is set."""
            return (self._flags & hal.TalonSRXConst.kMotionProfileFlag_ActTraj_IsValid) != 0
    
        #: (:class:`.TrajectoryPoint`) The number of points in the low level Talon buffer.
        activePoint = None
    
        #: (SetValueMotionProfile) The current output mode of the motion profile executer (disabled, enabled, or hold).
        #: When changing the set() value in MP mode, it's important to check this signal to
        #: confirm the change takes effect before interacting with the top buffer.
        outputEnable = hal.TalonSRXConst.kMotionProfile_Disable
        

    kDelayForSolicitedSignals = 0.004

    def __init__(self, deviceNumber,
                 controlPeriodMs=None,
                 enablePeriodMs=None):
        MotorSafety.__init__(self)

        self.pidSource = self.PIDSourceType.kDisplacement
        self.deviceNumber = deviceNumber
        
        # HAL bounds period to be within [1 ms,95 ms]
        if controlPeriodMs is None:
            self._handle = hal.TalonSRX_Create1(deviceNumber)
        elif enablePeriodMs is None:
            self._handle = hal.TalonSRX_Create2(deviceNumber, controlPeriodMs)
        else:
            self._handle = hal.TalonSRX_Create3(deviceNumber, controlPeriodMs, enablePeriodMs)
            
        self.__finalizer = weakref.finalize(self, _freeCANTalon,
                                                  self._handle)
        self.controlMode = self.ControlMode.PercentVbus 
        self.minimumInput = 0
        self.maximumInput = 0
        self.controlEnabled = True
        self.stopped = False
        self.isInverted = False
        self.profile = 0
        self.setPoint = 0.0
        self.codesPerRev = 0
        self.numPotTurns = 0
        self.feedbackDevice = self.FeedbackDevice.QuadEncoder
        self.setProfile(self.profile)
        self._applyControlMode(self.ControlMode.PercentVbus)
        
        LiveWindow.addActuatorChannel("CANTalon", deviceNumber, self)
        hal.HALReport(hal.HALUsageReporting.kResourceType_CANTalonSRX,
                      deviceNumber)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

    @property
    def handle(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use CANTalonSRX after free() has been called")
        return self._handle

    def free(self):
        LiveWindow.removeComponent(self)
        self.__finalizer()

    def pidWrite(self, output):
        if self.getControlMode() == self.ControlMode.PercentVbus:
            self.set(output)
        else:
            raise ValueError("PID only supported in PercentVbus mode")
        
    def setPIDSourceType(self, pidSource):
        self.pidSource = pidSource
        
    def getPIDSourceType(self):
        return self.pidSource
    
    def pidGet(self):
        return self.getPosition()

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
        self.feed()
        
        if self.stopped:
            self.enableControl()
            self.stopped = False
            
        if not self.controlEnabled:
            return
        
        self.setPoint = outputValue # cache set point for getSetpoint()
        
        if self.controlMode == self.ControlMode.PercentVbus:
            hal.TalonSRX_Set(self.handle, -outputValue if self.isInverted else outputValue)
        elif self.controlMode == self.ControlMode.Follower:
            hal.TalonSRX_SetDemand(self.handle, int(outputValue))
        elif self.controlMode == self.ControlMode.Voltage:
            # Voltage is an 8.8 fixed point number.
            volts = int((-outputValue if self.isInverted else outputValue) * 256)
            hal.TalonSRX_SetDemand(self.handle, volts)
        elif self.controlMode == self.ControlMode.Speed:
            hal.TalonSRX_SetDemand(self.handle, self._scaleVelocityToNativeUnits(self.feedbackDevice, -outputValue if self.isInverted else outputValue))
        elif self.controlMode == self.ControlMode.Position:
            hal.TalonSRX_SetDemand(self.handle, self._scaleRotationsToNativeUnits(self.feedbackDevice, -outputValue if self.isInverted else outputValue))
        elif self.controlMode == self.ControlMode.Current:
            mA = (-outputValue if self.isInverted else outputValue) * 1000.0; # mA
            hal.TalonSRX_SetDemand(self.handle, int(mA))
        elif self.controlMode == self.ControlMode.MotionProfile:
            hal.TalonSRX_SetDemand(self.handle, outputValue)
            
        hal.TalonSRX_SetModeSelect(self.handle, self.controlMode)
        
    def setInverted(self, isInverted):
        """
        Inverts the direction of the motor's rotation. Only works in PercentVbus
        mode.

        :param isInverted: The state of inversion (True is inverted).
        """
        self.isInverted = bool(isInverted)

    def getInverted(self):
        """
        Common interface for the inverting direction of a speed controller.

        :returns: The state of inversion (True is inverted).
        """
        return self.isInverted
    
    def reset(self):
        """Resets the accumulated integral error and disables the controller.
        
        The only difference between this and {@link PIDController#reset} is that
        the PIDController also resets the previous error for the D term, but the
        difference should have minimal effect as it will only last one cycle.
        """
        self.disable()
        self.clearIaccum()
        
    def isEnabled(self):
        """Return true if Talon is enabled.
        
        :returns: true if the Talon is enabled and may be applying power to the motor
        """
        return self.isControlEnabled()
    
    def getError(self):
        """Returns the difference between the setpoint and the current position.
        
        :returns: The error in units corresponding to whichever mode we are in.
        
        .. seealso:: :meth:`set` for a detailed description of the various units.
        """
        return self.getClosedLoopError()
    
    def setSetpoint(self, setpoint):
        """Calls :meth:`set`"""
        self.set(setpoint)

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

        In Position mode: returns current sensor position.

        In Throttle and Follower modes: returns current applied throttle.

        :returns: The current sensor value of the Talon.
        """
        if self.controlMode == self.ControlMode.Voltage:
            return self.getOutputVoltage()
        elif self.controlMode == self.ControlMode.Current:
            return self.getOutputCurrent()
        elif self.controlMode == self.ControlMode.Speed:
            return self._scaleNativeUnitsToRpm(self.feedbackDevice, hal.TalonSRX_GetSensorVelocity(self.handle))
        elif self.controlMode == self.ControlMode.Position:
            return self._scaleNativeUnitsToRotations(self.feedbackDevice, hal.TalonSRX_GetSensorPosition(self.handle))
        else: # PercentVbus
            return hal.TalonSRX_GetAppliedThrottle(self.handle) / 1023.0

    def getEncPosition(self):
        """
        Get the current encoder position, regardless of whether it is the
        current feedback device.

        :returns: The current position of the encoder.
        """
        return hal.TalonSRX_GetEncPosition(self.handle)
    
    def setEncPosition(self, newPosition):
        self.setParameter(hal.TalonSRXParam.eEncPosition, newPosition)

    def getEncVelocity(self):
        """
        Get the current encoder velocity, regardless of whether it is the
        current feedback device.

        :returns: The current speed of the encoder.
        """
        return hal.TalonSRX_GetEncVel(self.handle)
    
    def getPulseWidthPosition(self):
        return hal.TalonSRX_GetPulseWidthPosition(self.handle)
    
    def setPulseWidthPosition(self, newPosition):
        self.setParameter(hal.TalonSRXParam.ePwdPosition, newPosition)
        
    def getPulseWidthVelocity(self):
        return hal.TalonSRX_GetPulseWidthVelocity(self.handle)
    
    def getPulseWidthRiseToFallUs(self):
        return hal.TalonSRX_GetPulseWidthRiseToFallUs(self.handle)
  
    def getPulseWidthRiseToRiseUs(self):
        return hal.TalonSRX_GetPulseWidthRiseToRiseUs(self.handle)
    
    def isSensorPresent(self, feedbackDevice):
        """:param feedbackDevice: which feedback sensor to check it if is connected.
        :returns: status of caller's specified sensor type.
        """
        retval = self.FeedbackDeviceStatus.Unknown;
        # detecting sensor health depends on which sensor caller cares about
        if feedbackDevice in [self.FeedbackDevice.QuadEncoder,
                              self.FeedbackDevice.AnalogPot,
                              self.FeedbackDevice.AnalogEncoder,
                              self.FeedbackDevice.EncRising,
                              self.FeedbackDevice.EncFalling]:
            # no real good way to tell if these sensor
            # are actually present so return status unknown.
            pass
        elif feedbackDevice in [self.FeedbackDevice.PulseWidth,
                                self.FeedbackDevice.CtreMagEncoder_Relative,
                                self.FeedbackDevice.CtreMagEncoder_Absolute]:
            # all of these require pulse width signal to be present.
            if hal.TalonSRX_IsPulseWidthSensorPresent(self.handle) == 0:
                # Talon not getting a signal
                retval = self.FeedbackDeviceStatus.NotPresent;
            else:
                # getting good signal
                retval = self.FeedbackDeviceStatus.Present;
        
        return retval;

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
    
    def setAnalogPosition(self, newPosition):
        self.setParameter(hal.TalonSRXParam.eAinPosition, newPosition)

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

    def setAllowableClosedLoopErr(self, allowableCloseLoopError):
        """Set the allowable closed loop error.
        
        :param allowableCloseLoopError: allowable closed loop error for selected profile.
                                        mA for Curent closed loop.
                                        Talon Native Units for position and velocity.
        """
        if self.profile == 0:
            self.setParameter(hal.TalonSRXParam.eProfileParamSlot0_AllowableClosedLoopErr, allowableCloseLoopError)
        else:
            self.setParameter(hal.TalonSRXParam.eProfileParamSlot1_AllowableClosedLoopErr, allowableCloseLoopError)

    def isFwdLimitSwitchClosed(self):
        """Returns True if limit switch is closed. False if open."""
        return hal.TalonSRX_GetLimitSwitchClosedFor(self.handle) == 0

    def isRevLimitSwitchClosed(self):
        """Returns True if limit switch is closed. False if open."""
        return hal.TalonSRX_GetLimitSwitchClosedRev(self.handle) == 0

    def getBrakeEnableDuringNeutral(self):
        """Returns True if break is enabled during neutral. False if coast."""
        return hal.TalonSRX_GetBrakeIsEnabled(self.handle) != 0
    
    def configEncoderCodesPerRev(self, codesPerRev):
        """Configure how many codes per revolution are generated by your encoder.
        
        :param codesPerRev: The number of counts per revolution.
        """
        # first save the scalar so that all getters/setter work as the user expects
        self.codesPerRev = codesPerRev
        # next send the scalar to the Talon over CAN.  This is so that the Talon can report
        # it to whoever needs it, like the webdash.  Don't bother checking the return,
        # this is only for instrumentation and is not necessary for Talon functionality.
        self.setParameter(hal.TalonSRXParam.eNumberEncoderCPR, self.codesPerRev)
    
    def configPotentiometerTurns(self, turns):
        """Configure the number of turns on the potentiometer.
        
        :param turns: The number of turns of the potentiometer.
        """
        # first save the scalar so that all getters/setter work as the user expects
        self.numPotTurns = turns
        # next send the scalar to the Talon over CAN.  This is so that the Talon can report
        # it to whoever needs it, like the webdash.  Don't bother checking the return,
        # this is only for instrumentation and is not necessary for Talon functionality.
        self.setParameter(hal.TalonSRXParam.eNumberPotTurns, self.numPotTurns)

    def getTemperature(self):
        """Returns temperature of Talon, in degrees Celsius."""
        return hal.TalonSRX_GetTemp(self.handle)
    
    # deprecated
    getTemp = getTemperature

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
        """
        :returns: The position of the sensor currently providing feedback. When using
                    analog sensors, 0 units corresponds to 0V, 1023 units corresponds
                    to 3.3V When using an analog encoder (wrapping around 1023 to 0 is
                    possible) the units are still 3.3V per 1023 units. When using
                    quadrature, each unit is a quadrature edge (4X) mode.
        """
        return self._scaleNativeUnitsToRotations(self.feedbackDevice, hal.TalonSRX_GetSensorPosition(self.handle))

    def setPosition(self, pos):
        nativePos = self._scaleRotationsToNativeUnits(self.feedbackDevice, pos)
        hal.TalonSRX_SetSensorPosition(self.handle, nativePos)

    def getSpeed(self):
        """:returns: The speed of the sensor currently providing feedback.
        
        The speed units will be in the sensor's native ticks per 100ms.
        
        For analog sensors, 3.3V corresponds to 1023 units. So a speed of
        200 equates to ~0.645 dV per 100ms or 6.451 dV per second. If this
        is an analog encoder, that likely means 1.9548 rotations per sec.
        For quadrature encoders, each unit corresponds a quadrature edge
        (4X). So a 250 count encoder will produce 1000 edge events per
        rotation. An example speed of 200 would then equate to 20% of a
        rotation per 100ms, or 10 rotations per second.
        """
        return self._scaleNativeUnitsToRpm(self.feedbackDevice, hal.TalonSRX_GetSensorVelocity(self.handle))

    def getControlMode(self):
        return self.controlMode
    
    def setControlMode(self, controlMode):
        self.changeControlMode(controlMode)

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
        # save the selection so that future setters/getters know which scalars to apply
        self.feedbackDevice = device
        # pass feedback to actual CAN frame
        hal.TalonSRX_SetFeedbackDeviceSelect(self.handle, device)

    def setStatusFrameRateMs(self, stateFrame, periodMs):
        """Change the periodMs of a TALON's status frame.  See StatusFrameRate
        enum for what's available."""
        hal.TalonSRX_SetStatusFrameRate(self.handle, stateFrame, periodMs)

    def enableControl(self):
        self.changeControlMode(self.controlMode)
        self.controlEnabled = True
        
    def enable(self):
        self.enableControl()

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
        
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_P)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_P)

    def getI(self):
        """
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_I)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_I)

    def getD(self):
        """
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_D)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_D)

    def getF(self):
        """
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        if self.profile == 0:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot0_F)
        else:
            return self._getParam(hal.TalonSRXParam.eProfileParamSlot1_F)

    def getIZone(self):
        """
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
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
        
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        if self.profile == 0:
            throttlePerMs = self._getParamInt(hal.TalonSRXParam.eProfileParamSlot0_CloseLoopRampRate)
        else:
            throttlePerMs = self._getParamInt(hal.TalonSRXParam.eProfileParamSlot1_CloseLoopRampRate)

        return throttlePerMs / 1023.0 * 12.0 * 1000.0

    def getFirmwareVersion(self):
        """
        :returns: The version of the firmware running on the Talon
        
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        return self._getParamInt(hal.TalonSRXParam.eFirmVers)

    def getIaccum(self):
        """
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
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
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        hal.TalonSRX_SetPgain(self.handle, self.profile, p)

    def setI(self, i):
        """
        Set the integration constant of the currently selected profile.

        :param i: Integration constant for the currently selected PID profile.
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        hal.TalonSRX_SetIgain(self.handle, self.profile, i)

    def setD(self, d):
        """
        Set the derivative constant of the currently selected profile.

        :param d: Derivative constant for the currently selected PID profile.
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        hal.TalonSRX_SetDgain(self.handle, self.profile, d)

    def setF(self, f):
        """
        Set the feedforward value of the currently selected profile.

        :param f: Feedforward constant for the currently selected PID profile.
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        hal.TalonSRX_SetFgain(self.handle, self.profile, f)

    def setIZone(self, izone):
        """
        Set the integration zone of the current Closed Loop profile.

        Whenever the error is larger than the izone value, the accumulated
        integration error is cleared so that high errors aren't racked up when
        at high errors.

        An izone value of 0 means no difference from a standard PIDF loop.

        :param izone: Width of the integration zone.
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        hal.TalonSRX_SetIzone(self.handle, self.profile, izone)

    def setCloseLoopRampRate(self, rampRate):
        """
        Set the closed loop ramp rate for the current profile.

        Limits the rate at which the throttle will change.
        Only affects position and speed closed loop modes.

        :param rampRate: Maximum change in voltage, in volts / sec.
        :see: :meth:`setProfile` For selecting a certain profile.
        """
        # CanTalonSRX takes units of Throttle (0 - 1023) / 1ms.
        rate = int(rampRate * 1023.0 / 12.0 / 1000.0)
        hal.TalonSRX_SetCloseLoopRampRate(self.handle, self.profile, rate)

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
        
    def setVoltageCompensationRampRate(self, rampRate) :
        hal.TalonSRX_SetVoltageCompensationRate(self.handle, rampRate / 1000)

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
        
        :param profile: Selected profile (0 or 1)
        :type profile: int
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
        self.stopped = True

    def disable(self):
        self.disableControl()

    def getDeviceID(self):
        return self.deviceNumber

    # TODO: Documentation for all these accessors/setters for misc. stuff.

    def setForwardSoftLimit(self, forwardLimit):
        nativeLimitPos = self._scaleRotationsToNativeUnits(self.feedbackDevice, forwardLimit)
        hal.TalonSRX_SetForwardSoftLimit(self.handle, nativeLimitPos)
        
    def getForwardSoftLimit(self):
        return hal.TalonSRX_GetForwardSoftLimit(self.handle)

    def enableForwardSoftLimit(self, enable):
        hal.TalonSRX_SetForwardSoftEnable(self.handle, 1 if enable else 0)
        
    def isForwardSoftLimitEnabled(self):
        return hal.TalonSRX_GetForwardSoftEnable(self.handle) != 0

    def setReverseSoftLimit(self, reverseLimit):
        nativeLimitPos = self._scaleRotationsToNativeUnits(self.feedbackDevice, reverseLimit)
        hal.TalonSRX_SetReverseSoftLimit(self.handle, nativeLimitPos)
        
    def getReverseSoftLimit(self):
        return hal.TalonSRX_GetReverseSoftLimit(self.handle)

    def enableReverseSoftLimit(self, enable):
        hal.TalonSRX_SetReverseSoftEnable(self.handle, 1 if enable else 0)
    
    def isReverseSoftLimitEnabled(self):
        return hal.TalonSRX_GetReverseSoftEnable(self.handle) != 0
    
    def configMaxOutputVoltage(self, voltage):
        """Configure the maximum voltage that the Jaguar will ever output.
        
        This can be used to limit the maximum output voltage in all modes so that
        motors which cannot withstand full bus voltage can be used safely.
        
        :param voltage: The maximum voltage output by the Jaguar.
        """
        self.configPeakOutputVoltage(voltage, -voltage)
        
    def configPeakOutputVoltage(self, forwardVoltage, reverseVoltage):
        # bounds checking
        if forwardVoltage > 12:
            forwardVoltage = 12
        elif forwardVoltage < 0:
            forwardVoltage = 0
        if reverseVoltage > 0:
            reverseVoltage = 0
        elif reverseVoltage < -12:
            reverseVoltage = -12
        
        # config calls
        self.setParameter(hal.TalonSRXParam.ePeakPosOutput,1023*forwardVoltage/12.0)
        self.setParameter(hal.TalonSRXParam.ePeakNegOutput,1023*reverseVoltage/12.0)
      
    def configNominalOutputVoltage(self, forwardVoltage, reverseVoltage):
        # bounds checking
        if forwardVoltage > 12:
            forwardVoltage = 12
        elif forwardVoltage < 0:
            forwardVoltage = 0
        if reverseVoltage > 0:
            reverseVoltage = 0
        elif reverseVoltage < -12:
            reverseVoltage = -12
        
        # config calls
        self.setParameter(hal.TalonSRXParam.eNominalPosOutput,1023*forwardVoltage/12.0)
        self.setParameter(hal.TalonSRXParam.eNominalNegOutput,1023*reverseVoltage/12.0)

    def setParameter(self, param, value):
        """General set frame.  Since the parameter is a general integral type, this can
        be used for testing future features.
        """
        hal.TalonSRX_SetParam(self.handle, param, value)
        
    def getParameter(self, param):
        """General get frame.  Since the parameter is a general integral type, this can
        be used for testing future features.
        
        .. warning:: Calls Timer.delay(:const:`kDelayForSolicitedSignals`)
        """
        hal.TalonSRX_RequestParam(self.handle, param)
        Timer.delay(self.kDelayForSolicitedSignals)
        return hal.TalonSRX_GetParamResponse(self.handle, param)

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

    # Internal helper function
    
    
    def _getNativeUnitsPerRotationScalar(self, devToLookup):
        """:returns: Number of native units per rotation if scaling info is available.
        Zero if scaling information is not available.
        """
        retval = 0
        scalingAvail = False
        if devToLookup == self.FeedbackDevice.QuadEncoder:
            # When caller wants to lookup Quadrature, the QEI may be in 1x if the selected feedback is edge counter.
            # Additionally if the quadrature source is the CTRE Mag encoder, then the CPR is known.
            # This is nice in that the calling app does not require knowing the CPR at all.
            # So do both checks here.
            qeiPulsePerCount = 4  # default to 4x
            if self.feedbackDevice in [self.FeedbackDevice.CtreMagEncoder_Relative,
                                       self.FeedbackDevice.CtreMagEncoder_Absolute]:
                # we assume the quadrature signal comes from the MagEnc,
                # of which we know the CPR already
                retval = self.kNativePwdUnitsPerRotation
                scalingAvail = True
            elif self.feedbackDevice in [self.FeedbackDevice.EncRising, # Talon's QEI is setup for 1x, so perform 1x math
                                         self.FeedbackDevice.EncFalling]:
                qeiPulsePerCount = 1
              
            # QuadEncoder: Talon's QEI is 4x
            # pulse width and everything else, assume its regular quad use.
                
          
            if scalingAvail:
                # already deduced the scalar above, we're done.
                pass
            else:
                # we couldn't deduce the scalar just based on the selection
                if 0 == self.codesPerRev:
                    # caller has never set the CPR.  Most likely caller
                    # is just using engineering units so fall to the
                    # bottom of this func
                    pass
                else:
                    # Talon expects PPR units
                    retval = qeiPulsePerCount * self.codesPerRev
                    scalingAvail = True
            
        elif devToLookup in [self.FeedbackDevice.EncRising,
                             self.FeedbackDevice.EncFalling]:
            if 0 == self.codesPerRev:
                # caller has never set the CPR.  Most likely caller
                # is just using engineering units so fall to the
                # bottom of this func.
                pass
            else:
                # Talon expects PPR units
                retval = 1 * self.codesPerRev
                scalingAvail = True
            
        elif devToLookup in [self.FeedbackDevice.AnalogPot,
                             self.FeedbackDevice.AnalogEncoder]:
            if 0 == self.numPotTurns:
                # caller has never set the CPR.  Most likely caller
                # is just using engineering units so fall to the
                # bottom of this func.
                pass
            else :
                retval = self.kNativeAdcUnitsPerRotation / self.numPotTurns
                scalingAvail = True
        
        elif devToLookup in [self.FeedbackDevice.CtreMagEncoder_Relative,
                             self.FeedbackDevice.CtreMagEncoder_Absolute,
                             self.FeedbackDevice.PulseWidth]:
            retval = self.kNativePwdUnitsPerRotation
            scalingAvail = True
            
        # if scaling info is not available give caller zero
        if False == scalingAvail:
            return 0
        return retval
    
    def _scaleRotationsToNativeUnits(self, devToLookup, fullRotations):
        """:param fullRotations: double precision value representing number of rotations of selected feedback sensor.
        
                                 If user has never called the config routine for the selected sensor, then the caller
                                 is likely passing rotations in engineering units already, in which case it is returned
                                 as is.
        
        .. seealso:: :meth:`configPotentiometerTurns`, :meth:`configEncoderCodesPerRev`
        
        :returns: fullRotations in native engineering units of the Talon SRX firmware.
        """
        
        # first assume we don't have config info, prep the default return
        retval = fullRotations
        # retrieve scaling info
        scalar = self._getNativeUnitsPerRotationScalar(devToLookup)
        # apply scalar if its available
        if scalar > 0:
            retval = fullRotations*scalar
        return int(retval)
    
    def _scaleVelocityToNativeUnits(self, devToLookup, rpm):
        """:param rpm: double precision value representing number of rotations per minute of selected feedback sensor.
        
                       If user has never called the config routine for the selected sensor, then the caller
                       is likely passing rotations in engineering units already, in which case it is returned
                       as is.
        
        .. seealso:: :meth:`configPotentiometerTurns`, :meth:`configEncoderCodesPerRev`
        
        :returns: sensor velocity in native engineering units of the Talon SRX firmware.
        """
        
        # first assume we don't have config info, prep the default return
        retval = rpm
        # retrieve scaling info
        scalar = self._getNativeUnitsPerRotationScalar(devToLookup)
        # apply scalar if its available
        if scalar > 0:
            retval = rpm*scalar
        return int(retval)
    
    def _scaleNativeUnitsToRotations(self, devToLookup, nativePos):
        """:param nativePos: integral position of the feedback sensor in native Talon SRX units.
                             If user has never called the config routine for the selected sensor, then the return
                             will be in TALON SRX units as well to match the behavior in the 2015 season.
                             
        .. seealso:: :meth:`configPotentiometerTurns`, :meth:`configEncoderCodesPerRev`
        
        :returns: double precision number of rotations, unless config was never performed.
        """
        
        # first assume we don't have config info, prep the default return
        retval = float(nativePos)
        # retrieve scaling info
        scalar = self._getNativeUnitsPerRotationScalar(devToLookup)
        # apply scalar if its available
        if scalar > 0:
            retval = nativePos / scalar
        return retval
    
    def _scaleNativeUnitsToRpm(self, devToLookup, nativeVel):
        """:param nativeVel: integral velocity of the feedback sensor in native Talon SRX units.
                             If user has never called the config routine for the selected sensor, then the return
                             will be in TALON SRX units as well to match the behavior in the 2015 season.
                             
        .. seealso:: :meth:`configPotentiometerTurns`, :meth:`configEncoderCodesPerRev`
        
        :returns: double precision of sensor velocity in RPM, unless config was never performed.
        """
        
        # first assume we don't have config info, prep the default return
        retval = float(nativeVel)
        # retrieve scaling info
        scalar = self._getNativeUnitsPerRotationScalar(devToLookup)
        # apply scalar if its available
        if scalar > 0:
            retval = nativeVel / (self.kMinutesPer100msUnit*scalar)
        return retval
    
    def enableZeroSensorPositionOnIndex(self, enable, risingEdge):
        """Enables Talon SRX to automatically zero the Sensor Position whenever an
        edge is detected on the index signal.
        
        :param enable: boolean input, pass true to enable feature or false to disable.
        :type enable: bool
        :param risingEdge: boolean input, pass true to clear the position on rising edge,
        
                           pass false to clear the position on falling edge.
        :type risingEdge: bool
        """
        if enable:
            # enable the feature, update the edge polarity first to ensure
            # it is correct before the feature is enabled.
            self.setParameter(hal.TalonSRXParam.eQuadIdxPolarity, 1 if risingEdge else 0)
            self.setParameter(hal.TalonSRXParam.eClearPositionOnIdx, 1)
        else:
            # disable the feature first, then update the edge polarity.
            self.setParameter(hal.TalonSRXParam.eClearPositionOnIdx, 0)
            self.setParameter(hal.TalonSRXParam.eQuadIdxPolarity, 1 if risingEdge else 0)
            
    def changeMotionControlFramePeriod(self, periodMs):
        """Calling application can opt to speed up the handshaking between the robot API and the Talon to increase the
        download rate of the Talon's Motion Profile.  Ideally the period should be no more than half the period
        of a trajectory point.
        """
        hal.TalonSRX_ChangeMotionControlFramePeriod(self.handle, periodMs)
        
    def clearMotionProfileTrajectories(self):
        """Clear the buffered motion profile in both Talon RAM (bottom), and in the API (top).
        Be sure to check :meth:`getMotionProfileStatus` to know when the buffer is actually cleared.
        """
        hal.TalonSRX_ClearMotionProfileTrajectories(self.handle)
    
    def getMotionProfileTopLevelBufferCount(self):
        """Retrieve just the buffer count for the api-level (top) buffer.
        This routine performs no CAN or data structure lookups, so its fast and ideal
        if caller needs to quickly poll the progress of trajectory points being emptied
        into Talon's RAM. Otherwise just use :meth:`getMotionProfileStatus`.
        
        :returns: number of trajectory points in the top buffer.
        """
        return hal.TalonSRX_GetMotionProfileTopLevelBufferCount(self.handle)
    
    def pushMotionProfileTrajectory(self, trajPt):
        """Push another trajectory point into the top level buffer (which is emptied into
        the Talon's bottom buffer as room allows).
        
        :param targPos: servo position in native Talon units (sensor units).
        :param targVel: velocity to feed-forward in native Talon units (sensor units per 100ms).
        :param profileSlotSelect: which slot to pull PIDF gains from.  Currently supports 0 or 1.
        :param timeDurMs: time in milliseconds of how long to apply this point.
        :param velOnly: set to nonzero to signal Talon that only the feed-foward velocity should be
                        used, i.e. do not perform PID on position.  This is equivalent to setting
                        PID gains to zero, but much more efficient and synchronized to MP.
        :param isLastPoint: set to nonzero to signal Talon to keep processing this trajectory point,
                            instead of jumping to the next one when timeDurMs expires.  Otherwise
                            MP executer will eventuall see an empty buffer after the last point expires,
                            causing it to assert the IsUnderRun flag.  However this may be desired
                            if calling application nevers wants to terminate the MP.
        :param zeroPos: set to nonzero to signal Talon to "zero" the selected position sensor before executing
                        this trajectory point.  Typically the first point should have this set only thus allowing
                        the remainder of the MP positions to be relative to zero.
                        
        :returns: True if trajectory point push ok. False if buffer is full due to kMotionProfileTopBufferCapacity.
        """
        # check if there is room 
        if self.isMotionProfileTopLevelBufferFull():
            return False
        
        # convert position and velocity to native units
        targPos  = self._scaleRotationsToNativeUnits(self.feedbackDevice, trajPt.position)
        targVel = self._scaleVelocityToNativeUnits(self.feedbackDevice, trajPt.velocity)
        # bounds check signals that require it
        profileSlotSelect = 1 if trajPt.profileSlotSelect > 0 else 0
        timeDurMs = trajPt.timeDurMs
        # cap time to [0ms, 255ms], 0 and 1 are both interpreted as 1ms.
        if timeDurMs > 255:
            timeDurMs = 255
        if timeDurMs < 0:
            timeDurMs = 0
        # send it to the top level buffer
        hal.TalonSRX_PushMotionProfileTrajectory(self.handle, targPos, targVel, profileSlotSelect, timeDurMs,
                                                 1 if trajPt.velocityOnly else 0,
                                                 1 if trajPt.isLastPoint else 0,
                                                 1 if trajPt.zeroPos else 0)
        return True
    
    def isMotionProfileTopLevelBufferFull(self):
        """:returns: true if api-level (top) buffer is full."""
        return hal.TalonSRX_IsMotionProfileTopLevelBufferFull(self.handle)
    
    def processMotionProfileBuffer(self):
        """This must be called periodically to funnel the trajectory points from the API's top level buffer to
        the Talon's bottom level buffer.  Recommendation is to call this twice as fast as the executation rate of the motion profile.
        So if MP is running with 20ms trajectory points, try calling this routine every 10ms.  All motion profile functions are thread-safe
        through the use of a mutex, so there is no harm in having the caller utilize threading.
        """
        hal.TalonSRX_ProcessMotionProfileBuffer(self.handle)
        
    def getMotionProfileStatus(self, motionProfileStatus):
        """Retrieve all Motion Profile status information.
        
        Since this all comes from one CAN frame, its ideal to have one routine to retrieve the frame once and decode everything.
        
        :param motionProfileStatus: contains all progress information on the currently running MP.  Caller should
                                    must instantiate the motionProfileStatus object first then pass into this routine to be filled.
        :type motionProfileStatus: :class:`.MotionProfileStatus`
        """
        if motionProfileStatus.activePoint is None:
            motionProfileStatus.activePoint = self.TrajectoryPoint()
        
        flags, \
        motionProfileStatus.activePoint.profileSlotSelect, \
        targPos, targVel, \
        motionProfileStatus.topBufferRem, \
        motionProfileStatus.topBufferCnt, \
        motionProfileStatus.btmBufferCnt, \
        motionProfileStatus.outputEnable = \
            hal.TalonSRX_GetMotionProfileStatus(self.handle)
        
        motionProfileStatus._flags = flags
        motionProfileStatus.activePoint.isLastPoint = (flags & hal.TalonSRXConst.kMotionProfileFlag_ActTraj_IsLast) > 0
        motionProfileStatus.activePoint.velocityOnly = (flags & hal.TalonSRXConst.kMotionProfileFlag_ActTraj_VelOnly) > 0
        motionProfileStatus.activePoint.position = self._scaleNativeUnitsToRotations(self.feedbackDevice, targPos)
        motionProfileStatus.activePoint.velocity = self._scaleNativeUnitsToRpm(self.feedbackDevice, targVel)
        motionProfileStatus.activePoint.zeroPos = False # this signal is only used sending pts to Talon
        motionProfileStatus.activePoint.timeDurMs = 0   # this signal is only used sending pts to Talon
    
    def clearMotionProfileHasUnderrun(self):
        """Clear the hasUnderrun flag in Talon's Motion Profile Executer when MPE is ready for another point,
        but the low level buffer is empty.
        
        Once the Motion Profile Executer sets the hasUnderrun flag, it stays set until
        Robot Application clears it with this routine, which ensures Robot Application
        gets a chance to instrument or react.  Caller could also check the isUnderrun flag
        which automatically clears when fault condition is removed.
        """
        self.setParameter(hal.TalonSRXParam.eMotionProfileHasUnderrunErr, 0)

    def getDescription(self):
        return "CANTalon ID %d" % self.deviceNumber
    
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
        self.set(0) # Stop for safety
        super().startLiveWindowMode()

    def stopLiveWindowMode(self):
        super().stopLiveWindowMode()
        self.set(0) # Stop for safety
    
