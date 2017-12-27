# validated: 2017-12-06 EN f9bece2ffbf7 edu/wpi/first/wpilibj/Compressor.java
import hal
from networktables import NetworkTables

from .sensorbase import SensorBase
from .sendablebase import SendableBase

__all__ = ["Compressor"]

class Compressor(SendableBase):
    """Class for operating a compressor connected to a PCM (Pneumatic Control Module).
    
    The PCM will automatically run in closed loop mode by default whenever a
    Solenoid object is created. For most cases the Compressor object does not
    need to be instantiated or used in a robot program. This class is only required 
    in cases where the robot program needs a more detailed status of the compressor or to
    enable/disable closed loop control.

    Note: you cannot operate the compressor directly from this class as doing
    so would circumvent the safety provided by using the pressure switch and closed loop control.
    You can only turn off closed loop control, thereby stopping the compressor from operating.
    """

    def __init__(self, module=None):
        """Makes a new instance of the compressor using the provided CAN device ID.
        
        :param module: The PCM CAN device ID. (0 - 62 inclusive)
        """
        super().__init__()
        self.table = None
        if module is None:
            module = SensorBase.getDefaultSolenoidModule()
        self.compressorHandle = hal.initializeCompressor(module)
        hal.report(hal.UsageReporting.kResourceType_Compressor, module)
        self.setName("Compressor", module)
        self.module = module

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
        return hal.getCompressor(self.compressorHandle)

    def getPressureSwitchValue(self):
        """ Get the pressure switch value.
 
        :returns: True if the pressure is low
        :rtype: bool
        """
        return hal.getCompressorPressureSwitch(self.compressorHandle)

    def getCompressorCurrent(self):
        """Get the current being used by the compressor.
        
        :returns: Current consumed by the compressor in amps
        :rtype: float
        """
        return hal.getCompressorCurrent(self.compressorHandle)

    def setClosedLoopControl(self, on):
        """Set the PCM in closed loop control mode.
        
        :param on: If True sets the compressor to be in closed loop control
                   mode (default)
        :type  on: bool
        """
        hal.setCompressorClosedLoopControl(self.compressorHandle, True if on else False)

    def getClosedLoopControl(self):
        """Gets the current operating mode of the PCM.
        
        :returns: True if compressor is operating on closed-loop mode
        :rtype: bool
        """
        return hal.getCompressorClosedLoopControl(self.compressorHandle)

    def getCompressorCurrentTooHighFault(self):
        """
        :returns: True if PCM is in fault state : Compressor Drive is
            disabled due to compressor current being too high
        """
        return hal.getCompressorCurrentTooHighFault(self.compressorHandle)

    def getCompressorCurrentTooHighStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor is
            disabled due to compressor current being too high
        """
        return hal.getCompressorCurrentTooHighStickyFault(self.compressorHandle)

    def getCompressorShortedFault(self):
        """
        :returns: True if PCM is in fault state : Compressor output
            appears to be shorted
        """
        return hal.getCompressorShortedFault(self.compressorHandle)

    def getCompressorShortedStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor output
            appears to be shorted
        """
        return hal.getCompressorShortedStickyFault(self.compressorHandle)

    def getCompressorNotConnectedFault(self):
        """
        :returns: True if PCM is in fault state : Compressor does not appear
            to be wired, i.e. compressor is not drawing enough current.
        """
        return hal.getCompressorNotConnectedFault(self.compressorHandle)

    def getCompressorNotConnectedStickyFault(self):
        """
        :returns: True if PCM sticky fault is set : Compressor does not appear
            to be wired, i.e. compressor is not drawing enough current.
        """
        return hal.getCompressorNotConnectedStickyFault(self.compressorHandle)

    def clearAllPCMStickyFaults(self):
        """Clear ALL sticky faults inside PCM that Compressor is wired to.

        If a sticky fault is set, then it will be persistently cleared. The compressor might 
        momentarily disable while the flags are being cleared. Doo not call this method too
        frequently, otherwise normal compressor functionality may be prevented.

        If no sticky faults are set then this call will have no effect.
        """
        hal.clearAllPCMStickyFaults(self.module)

    def initSendable(self, builder):
        builder.setSmartDashboardType("Compressor")
        builder.addBooleanProperty("Enabled", self.enabled, self.enabledChanged)
        builder.addBooleanProperty("Pressure switch", self.getPressureSwitchValue, None)

    def enabledChanged(self, value):
        if value:
            self.start()
        else:
            self.stop()
