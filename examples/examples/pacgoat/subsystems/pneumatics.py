import wpilib
from wpilib.command import Subsystem
from .. import robot


class Pneumatics(Subsystem):
    """
    The Pneumatics subsystem contains the compressor and a pressure sensor.

    NOTE: The simulator currently doesn't support the compressor or pressure sensors.
    """

    MAX_PRESSURE = 2.55

    def __init__(self):
        self.pressure_sensor = wpilib.AnalogInput(3)
        if robot.is_real():
            self.compressor = wpilib.Compressor()

        wpilib.LiveWindow.addSensor("Pneumatics", "Pressure Sensor", self.pressure_sensor)
        super().__init__()

    def initDefaultCommand(self):
        """No default command."""
        pass

    def start(self):
        """:return Whether or not the system is fully pressurized"""
        if robot.is_real():
            return self.MAX_PRESSURE <= self.pressure_sensor.getVoltage()
        else:
            return True

    def write_pressure(self):
        """Puts the pressure on the SmartDashboard."""
        wpilib.SmartDashboard.putNumber("Pressure", self.pressure_sensor.getVoltage())
