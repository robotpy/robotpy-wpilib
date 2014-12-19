import hal
import weakref

__all__ = ["CanTalonSRX"]

def _freeCanTalonSRX(handle):
    hal.TalonSRX_Destroy(handle)

class CanTalonSRX:
    """CAN TALON SRX driver.

    The TALON SRX is designed to instrument all runtime signals periodically.
    The default periods are chosen to support 16 TALONs with 10ms update rate
    for control (throttle or setpoint).  However these can be overridden with
    :meth:`setStatusFrameRate`. The getters for these
    unsolicited signals are auto generated at the bottom of this module.

    Likewise most control signals are sent periodically using the
    fire-and-forget CAN API.  The setters for these unsolicited signals are
    auto generated at the bottom of this module.

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
    ticks per rotation (0V => 3.3V).  Use :meth:`setFeedbackDeviceSelect` to select
    which sensor type you need.  Once you do that you can use
    :meth:`getSensorPosition` and :meth:`getSensorVelocity`.  These signals are updated on
    CANBus every 20ms (by default).  If a relative sensor is selected, you can
    zero (or change the current value) using :meth:`setSensorPosition`.

    Analog Input and quadrature position (and velocity) are also explicitly
    reported in :meth:`getEncPosition`, :meth:`getEncVel`, :meth:`getAnalogInWithOv`, :meth:`getAnalogInVel`.
    These signals are available all the time, regardless of what sensor is
    selected at a rate of 100ms.  This allows easy instrumentation for "in the
    pits" checking of all sensors regardless of modeselect.  The 100ms rate is
    overridable for teams who want to acquire sensor data for processing, not
    just instrumentation.  Or just select the sensor using
    :meth:`setFeedbackDeviceSelect` to get it at 20ms.

    Velocity is in position ticks / 100ms.

    All output units are in respect to duty cycle (throttle) which is
    -1023(full reverse) to +1023 (full forward).  This includes demand (which
    specifies duty cycle when in duty cycle mode) and rampRamp, which is in
    throttle units per 10ms (if nonzero).

    Pos and velocity close loops are calc'd as::

        err = target - posOrVel
        iErr += err
        if IZone != 0 and abs(err) > IZone:
            ClearIaccum()
        output = P * err + I * iErr + D * dErr + F * target
        dErr = err - lastErr

    P, I, and D gains are always positive. F can be negative.

    Motor direction can be reversed using :meth:`setRevMotDuringCloseLoopEn` if sensor
    and motor are out of phase.  Similarly feedback sensor can also be reversed
    (multiplied by -1) if you prefer the sensor to be inverted.

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

    def __init__(self, deviceNumber=0,
                 controlPeriodMs=hal.TalonSRXConst.kDefaultControlPeriodMs):
        self._handle = hal.TalonSRX_Create(deviceNumber, controlPeriodMs)
        self._handle_finalizer = weakref.finalize(self, _freeCanTalonSRX,
                                                  self._handle)

    @property
    def handle(self):
        if not self._handle_finalizer.alive:
            raise ValueError("operation on freed port")
        return self._handle

    def free(self):
        self._handle_finalizer()

    def set(self, value):
        if value > 1:
            value = 1
        elif value < -1:
            value = -1
        hal.TalonSRX_SetDemand(self.handle, 1023*value)

    def setParam(self, paramEnum, value):
        hal.TalonSRX_SetParam(self.handle, paramEnum, value)

    def requestParam(self, paramEnum):
        hal.TalonSRX_RequestParam(self.handle, paramEnum)

    def getParamResponse(self, paramEnum):
        return hal.TalonSRX_GetParamResponse(self.handle, paramEnum)

    def getParamResponseInt32(self, paramEnum):
        return hal.TalonSRX_GetParamResponseInt32(self.handle, paramEnum)

    # getters and setters that use param request/response.
    # These signals are backed up in flash and will survive a power cycle.
    # If your application requires changing these values consider using both
    # slots and switch between slot0 <=> slot1.
    # If your application requires changing these signals frequently then it
    # makes sense to leverage this API.
    # Getters don't block, so it may require several calls to get the latest
    # value.
    def setPgain(self, slotIdx, gain):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_P, gain)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_P, gain)

    def setIgain(self, slotIdx, gain):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_I, gain)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_I, gain)

    def setDgain(self, slotIdx, gain):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_D, gain)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_D, gain)

    def setFgain(self, slotIdx, gain):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_F, gain)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_F, gain)

    def setIzone(self, slotIdx, zone):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_IZone, zone)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_IZone, zone)

    def setCloseLoopRampRate(self, slotIdx, closeLoopRampRate):
        if slotIdx == 0:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot0_CloseLoopRampRate, closeLoopRampRate)
        else:
            hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSlot1_CloseLoopRampRate, closeLoopRampRate)

    def setSensorPosition(self, pos):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eSensorPosition, pos)

    def setForwardSoftLimit(self, forwardLimit):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForThreshold, forwardLimit)

    def setReverseSoftLimit(self, reverseLimit):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevThreshold, reverseLimit)

    def setForwardSoftEnable(self, enable):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForEnable, enable)

    def setReverseSoftEnable(self, enable):
        hal.TalonSRX_SetParam(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevEnable, enable)

    def getPgain(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot0_P)
        else:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot1_P)

    def getIgain(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot0_I)
        else:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot1_I)

    def getDgain(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot0_D)
        else:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot1_D)

    def getFgain(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot0_F)
        else:
            return hal.TalonSRX_GetParamResponse(self.handle, hal.TalonSRXParam.eProfileParamSlot1_F)

    def getIzone(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSlot0_IZone)
        else:
            return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSlot1_IZone)

    def getCloseLoopRampRate(self, slotIdx):
        if slotIdx == 0:
            return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSlot0_CloseLoopRampRate)
        else:
            return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSlot1_CloseLoopRampRate)

    def getForwardSoftLimit(self):
        return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForThreshold)

    def getReverseSoftLimit(self):
        return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevThreshold)

    def getForwardSoftEnable(self):
        return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitForEnable)

    def getReverseSoftEnable(self):
        return hal.TalonSRX_GetParamResponseInt32(self.handle, hal.TalonSRXParam.eProfileParamSoftLimitRevEnable)

    def setStatusFrameRate(self, frameEnum, periodMs):
        """Change the periodMs of a TALON's status frame.  See kStatusFrame_*
        enums for what's available."""
        hal.TalonSRX_SetStatusFrameRate(self.handle, frameEnum, periodMs)

    def clearStickyFaults(self):
        """Clear all sticky faults in TALON.
        """
        hal.TalonSRX_ClearStickyFaults(self.handle)

    # This API is optimal since it uses the fire-and-forget CAN interface
    # These signals should cover the majority of all use cases.
    def getFault_OverTemp(self):
        return hal.TalonSRX_GetFault_OverTemp(self.handle)

    def getFault_UnderVoltage(self):
        return hal.TalonSRX_GetFault_UnderVoltage(self.handle)

    def getFault_ForLim(self):
        return hal.TalonSRX_GetFault_ForLim(self.handle)

    def getFault_RevLim(self):
        return hal.TalonSRX_GetFault_RevLim(self.handle)

    def getFault_HardwareFailure(self):
        return hal.TalonSRX_GetFault_HardwareFailure(self.handle)

    def getFault_ForSoftLim(self):
        return hal.TalonSRX_GetFault_ForSoftLim(self.handle)

    def getFault_RevSoftLim(self):
        return hal.TalonSRX_GetFault_RevSoftLim(self.handle)

    def getStckyFault_OverTemp(self):
        return hal.TalonSRX_GetStckyFault_OverTemp(self.handle)

    def getStckyFault_UnderVoltage(self):
        return hal.TalonSRX_GetStckyFault_UnderVoltage(self.handle)

    def getStckyFault_ForLim(self):
        return hal.TalonSRX_GetStckyFault_ForLim(self.handle)

    def getStckyFault_RevLim(self):
        return hal.TalonSRX_GetStckyFault_RevLim(self.handle)

    def getStckyFault_ForSoftLim(self):
        return hal.TalonSRX_GetStckyFault_ForSoftLim(self.handle)

    def getStckyFault_RevSoftLim(self):
        return hal.TalonSRX_GetStckyFault_RevSoftLim(self.handle)

    def getAppliedThrottle(self):
        return hal.TalonSRX_GetAppliedThrottle(self.handle)

    def getCloseLoopErr(self):
        return hal.TalonSRX_GetCloseLoopErr(self.handle)

    def getFeedbackDeviceSelect(self):
        return hal.TalonSRX_GetFeedbackDeviceSelect(self.handle)

    def getModeSelect(self):
        return hal.TalonSRX_GetModeSelect(self.handle)

    def getLimitSwitchEn(self):
        return hal.TalonSRX_GetLimitSwitchEn(self.handle)

    def getLimitSwitchClosedFor(self):
        return hal.TalonSRX_GetLimitSwitchClosedFor(self.handle)

    def getLimitSwitchClosedRev(self):
        return hal.TalonSRX_GetLimitSwitchClosedRev(self.handle)

    def getSensorPosition(self):
        return hal.TalonSRX_GetSensorPosition(self.handle)

    def getSensorVelocity(self):
        return hal.TalonSRX_GetSensorVelocity(self.handle)

    def getCurrent(self, param):
        return hal.TalonSRX_GetCurrent(self.handle, param)

    def getBrakeIsEnabled(self):
        return hal.TalonSRX_GetBrakeIsEnabled(self.handle)

    def getEncPosition(self):
        return hal.TalonSRX_GetEncPosition(self.handle)

    def getEncVel(self):
        return hal.TalonSRX_GetEncVel(self.handle)

    def getEncIndexRiseEvents(self):
        return hal.TalonSRX_GetEncIndexRiseEvents(self.handle)

    def getQuadApin(self):
        return hal.TalonSRX_GetQuadApin(self.handle)

    def getQuadBpin(self):
        return hal.TalonSRX_GetQuadBpin(self.handle)

    def getQuadIdxpin(self):
        return hal.TalonSRX_GetQuadIdxpin(self.handle)

    def getAnalogInWithOv(self):
        return hal.TalonSRX_GetAnalogInWithOv(self.handle)

    def getAnalogInVel(self):
        return hal.TalonSRX_GetAnalogInVel(self.handle)

    def getTemp(self):
        return hal.TalonSRX_GetTemp(self.handle)

    def getBatteryV(self):
        return hal.TalonSRX_GetBatteryV(self.handle)

    def getResetCount(self):
        return hal.TalonSRX_GetResetCount(self.handle)

    def getResetFlags(self):
        return hal.TalonSRX_GetResetFlags(self.handle)

    def getFirmVers(self):
        return hal.TalonSRX_GetFirmVers(self.handle)

    def setDemand(self, param):
        hal.TalonSRX_SetDemand(self.handle, param)

    def setOverrideLimitSwitchEn(self, param):
        hal.TalonSRX_SetOverrideLimitSwitchEn(self.handle, param)

    def setFeedbackDeviceSelect(self, param):
        hal.TalonSRX_SetFeedbackDeviceSelect(self.handle, param)

    def setRevMotDuringCloseLoopEn(self, param):
        hal.TalonSRX_SetRevMotDuringCloseLoopEn(self.handle, param)

    def setOverrideBrakeType(self, param):
        hal.TalonSRX_SetOverrideBrakeType(self.handle, param)

    def setModeSelect(self, param):
        hal.TalonSRX_SetModeSelect(self.handle, param)

    def setProfileSlotSelect(self, param):
        hal.TalonSRX_SetProfileSlotSelect(self.handle, param)

    def setRampThrottle(self, param):
        hal.TalonSRX_SetRampThrottle(self.handle, param)

    def setRevFeedbackSensor(self, param):
        hal.TalonSRX_SetRevFeedbackSensor(self.handle, param)
