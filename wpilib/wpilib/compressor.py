import hal

from .sensorbase import SensorBase

__all__ = ["Compressor"]

class Compressor(SensorBase):
    """Operates the PCM (Pneumatics compressor module)
    
    The PCM automatically will run in close-loop mode by default whenever a
    Solenoid object is created. For most cases the Compressor object does not
    need to be instantiated or used in a robot program.

    This class is only required in cases where more detailed status or to
    enable/disable closed loop control. Note: you cannot operate the
    compressor directly from this class as doing so would circumvent the
    safety provided in using the pressure switch and closed loop control.
    You can only turn off closed loop control, thereby stopping the
    compressor from operating.
    
    .. not_implemented: initCompressor
    """

    def __init__(self, pcmId=None):
        """Create an instance of the Compressor
        
        :param pcmID: The PCM CAN device ID. Most robots that use PCM will
                      have a single module. Use this for supporting a second
                      module other than the default.
        """
        if pcmId is None:
            pcmId = SensorBase.getDefaultSolenoidModule()
        self.pcm = hal.initializeCompressor(pcmId)

    def start(self):
        """Start the compressor running in closed loop control mode.
        Use the method in cases where you would like to manually stop and
        start the compressor for applications such as conserving battery
        or making sure that the compressor motor doesn't start during
        critical operations.
        """
        self.setClosedLoopControl(True)

    def stop(self):
        """Stop the compressor from running in closed loop control mode.
        Use the method in cases where you would like to manually stop and
        start the compressor for applications such as conserving battery
        or making sure that the compressor motor doesn't start during
        critical operations.
        """
        self.setClosedLoopControl(False)

    def enabled(self):
        """Get the enabled status of the compressor.
        
        :returns: True if the compressor is on
        :rtype: bool
        """
        return hal.getCompressor(self.pcm)

    def getPressureSwitchValue(self):
        """Get the current pressure switch value.
        
        :returns: True if the pressure is low by reading the pressure switch
            that is plugged into the PCM
        :rtype: bool
        """
        return hal.getPressureSwitch(self.pcm)

    def getCompressorCurrent(self):
        """Get the current being used by the compressor.
        
        :returns: Current consumed in amps for the compressor motor
        :rtype: float
        """
        return hal.getCompressorCurrent(self.pcm)

    def setClosedLoopControl(self, on):
        """Set the PCM in closed loop control mode.
        
        :param on: If True sets the compressor to be in closed loop control
                   mode otherwise normal operation of the compressor is disabled.
        :type  on: bool
        """
        hal.setClosedLoopControl(self.pcm, on)

    def getClosedLoopControl(self):
        """Gets the current operating mode of the PCM.
        
        :returns: True if compressor is operating on closed-loop mode,
                  otherwise return False.
        :rtype: bool
        """
        return hal.getClosedLoopControl(self.pcm)

    def getCompressorCurrentTooHighFault(self):
        """
        :returns: True if PCM is in fault state : Compressor Drive is
            disabled due to compressor current being too high
        """
        return hal.getCompressorCurrentTooHighFault(self.pcm)

    def getCompressorCurrentTooHighStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor Drive is
            disabled due to compressor current being too high
        """
        return hal.getCompressorCurrentTooHighStickyFault(self.pcm)

    def getCompressorShortedFault(self):
        """
        :returns: True if PCM is in fault state : Compressor Output
            appears to be shorted
        """
        return hal.getCompressorShortedFault(self.pcm)

    def getCompressorShortedStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor Output
            appears to be shorted
        """
        return hal.getCompressorShortedStickyFault(self.pcm)

    def getCompressorNotConnectedFault(self):
        """
        :returns: True if PCM is in fault state : Compressor does not appear
            to be wired, i.e. compressor is not drawing enough current.
        """
        return hal.getCompressorNotConnectedFault(self.pcm)

    def getCompressorNotConnectedStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor does not appear
            to be wired, i.e. compressor is not drawing enough current.
        """
        return hal.getCompressorNotConnectedStickyFault(self.pcm)

    def clearAllPCMStickyFaults(self):
        hal.clearAllPCMStickyFaults(self.pcm)

    def getSmartDashboardType(self):
        return "Compressor"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putBoolean("Enabled", self.enabled())
            table.putBoolean("Pressure Switch", self.getPressureSwitchValue())
