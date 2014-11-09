import hal

from .sensorbase import SensorBase

__all__ = ["Compressor"]

class Compressor(SensorBase):
    """Class for operating the PCM (Pneumatics compressor module)
    The PCM automatically will run in close-loop mode by default whenever a
    Solenoid object is created. For most cases the Compressor object does not
    need to be instantiated or used in a robot program.

    This class is only required in cases where more detailed status or to
    enable/disable closed loop control. Note: you cannot operate the
    compressor directly from this class as doing so would circumvent the
    safety provided in using the pressure switch and closed loop control.
    You can only turn off closed loop control, thereby stopping the
    compressor from operating.
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
        """
        return hal.getCompressor(self.pcm)

    def getPressureSwitchValue(self):
        """Get the current pressure switch value.
        
        :returns: True if the pressure is low by reading the pressure switch
            that is plugged into the PCM
        """
        return hal.getPressureSwitch(self.pcm)

    def getCompressorCurrent(self):
        """Get the current being used by the compressor.
        
        :returns: Current consumed in amps for the compressor motor
        """
        return hal.getCompressorCurrent(self.pcm)

    def setClosedLoopControl(self, on):
        """Set the PCM in closed loop control mode.
        
        :param on: If True sets the compressor to be in closed loop control
                   mode otherwise normal operation of the compressor is disabled.
        """
        hal.setClosedLoopControl(self.pcm, on)

    def getClosedLoopControl(self):
        """Gets the current operating mode of the PCM.
        
        :returns: True if compressor is operating on closed-loop mode,
                  otherwise return False.
        """
        return hal.getClosedLoopControl(self.pcm)

    def getSmartDashboardType(self):
        return "Compressor"

    def updateTable(self):
        table = self.getTable()
        if table is not None:
            table.putBoolean("Enabled", self.enabled())
            table.putBoolean("Pressure Switch", self.getPressureSwitchValue())
