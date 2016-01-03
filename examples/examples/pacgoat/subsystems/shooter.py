import wpilib
from wpilib.command import Subsystem


class Shooter(Subsystem):
    """
    The Shooter subsystem handles shooting. The mechanism for shooting is
    slightly complicated because it has two pneumatic cylinders for shooting, and
    a third latch to allow the pressure to partially build up and reduce the
    effect of the airflow. For shorter shots, when full power isn't needed, only
    one cylinder fires.

    NOTE: Simulation currently approximates this as a single pneumatic cylinder
    and ignores the latch.
    """

    def __init__(self, robot):
        super().__init__()
        self.robot = robot

        # Configure Devices
        self.hotGoalSensor = wpilib.DigitalInput(8)
        self.piston1 = wpilib.DoubleSolenoid(0, 3, 4)
        self.piston2 = wpilib.DoubleSolenoid(0, 5, 6)
        self.latchPiston = wpilib.Solenoid(0, 2)
        self.piston1ReedSwitchFront = wpilib.DigitalInput(9)
        self.piston1ReedSwitchBack = wpilib.DigitalInput(11)

        # Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addSensor("Shooter", "Hot Goal Sensor",
                                    self.hotGoalSensor)
        wpilib.LiveWindow.addSensor("Shooter", "Piston1 Reed Switch Front",
                                    self.piston1ReedSwitchFront)
        wpilib.LiveWindow.addSensor("Shooter", "Piston1 Reed Switch Back",
                                    self.piston1ReedSwitchBack)
        wpilib.LiveWindow.addActuator("Shooter", "Latch Piston",
                                      self.latchPiston)
        

    def initDefaultCommand(self):
        """No default command."""
        pass

    def extendBoth(self):
        """Extend both solenoids to shoot."""
        self.piston1.set(wpilib.DoubleSolenoid.Value.kForward)
        self.piston2.set(wpilib.DoubleSolenoid.Value.kForward)

    def retractBoth(self):
        """Retract both solenoids to prepare to shoot."""
        self.piston1.set(wpilib.DoubleSolenoid.Value.kReverse)
        self.piston2.set(wpilib.DoubleSolenoid.Value.kReverse)

    def extend1(self):
        """Extend solenoid 1 to shoot."""
        self.piston1.set(wpilib.DoubleSolenoid.Value.kForward)

    def retract1(self):
        """Retract solenoid 1 to prepare to shoot."""
        self.piston1.set(wpilib.DoubleSolenoid.Value.kReverse)

    def extend2(self):
        """Extend solenoid 2 to shoot."""
        self.piston2.set(wpilib.DoubleSolenoid.Value.kReverse)

    def retract2(self):
        """Retract solenoid 2 to prepare to shoot."""
        self.piston2.set(wpilib.DoubleSolenoid.Value.kForward)

    def off1(self):
        """
        Turns off the piston1 double solenoid. This won't actuate anything
        because double solenoids preserve their state when turned off. This
        should be called in order to reduce the amount of time that the coils
        are powered.
        """
        self.piston1.set(wpilib.DoubleSolenoid.Value.kOff)

    def off2(self):
        """
        Turns off the piston2 double solenoid. This won't actuate anything
        because double solenoids preserve their state when turned off. This
        should be called in order to reduce the amount of time that the coils
        are powered.
        """
        self.piston2.set(wpilib.DoubleSolenoid.Value.kOff)

    def unlatch(self):
        """Release the latch so we can shoot."""
        self.latchPiston.set(True)

    def latch(self):
        """Latch so that pressure can build up and we aren't limited by air flow."""
        self.latchPiston.set(False)

    def toggle_latch_position(self):
        """Toggles the latch position"""
        self.latchPiston.set(not self.latchPiston.get())

    def piston1IsExtended(self):
        """:return Whether or not piston 1 is fully extended."""
        return not self.piston1ReedSwitchFront.get()

    def piston1IsRetracted(self):
        """:return Whether or not piston 1 is fully retracted."""
        return not self.piston1ReedSwitchBack.get()

    def offBoth(self):
        """
        Turns off all double solenoids. Double solenoids hold their position when
        they are turned off. We should turn them off whenever possible to extend
        the life of the coils.
        """
        self.piston1.set(wpilib.DoubleSolenoid.Value.kOff)
        self.piston2.set(wpilib.DoubleSolenoid.Value.kOff)

    def goalIsHot(self):
        """:return Whether or not the goal is hot as read by the banner sensor."""
        return self.hotGoalSensor.get()
