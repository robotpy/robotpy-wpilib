import wpilib
from wpilib.command import Subsystem

class Pneumatics(Subsystem):
    """
    The Pneumatics subsystem contains the compressor and a pressure sensor.

    NOTE: The simulator currently doesn't support the compressor or pressure sensors.
    """

    MAX_PRESSURE = 2.55

    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        
        self.pressureSensor = wpilib.AnalogInput(3)
        if robot.isReal():
            self.compressor = wpilib.Compressor()

        wpilib.LiveWindow.addSensor("Pneumatics", "Pressure Sensor", self.pressureSensor)
        

    def initDefaultCommand(self):
        """No default command."""
        pass

    def start(self):
        """Start the compressor going. The compressor automatically starts and
        stops as it goes above and below maximum pressure."""
        if self.robot.isReal():
            self.compressor.start()
        
    def isPressurized(self):
        """:return Whether or not the system is fully pressurized"""
        if self.robot.isReal():
            return self.MAX_PRESSURE <= self.pressureSensor.getVoltage()
        else:
            return True

    def writePressure(self):
        """Puts the pressure on the SmartDashboard."""
        wpilib.SmartDashboard.putNumber("Pressure", self.pressureSensor.getVoltage())
