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
        self.robot = robot

        #Configure Devices
        self.hot_goal_sensor = wpilib.DigitalInput(4)
        self.piston1 = wpilib.DoubleSolenoid(0, 2, 3)
        self.piston2 = wpilib.DoubleSolenoid(0, 4, 5)
        self.latch_piston = wpilib.Solenoid(0, 1)
        self.piston1_reed_switch_front = wpilib.DigitalInput(8)
        self.piston1_reed_switch_back = wpilib.DigitalInput(7)

        #Put everything to the LiveWindow for testing.
        wpilib.LiveWindow.addSensor("Shooter", "Hot Goal Sensor", self.hot_goal_sensor)
        wpilib.LiveWindow.addSensor("Shooter", "Piston1 Reed Switch Front", self.piston1_reed_switch_front)
        wpilib.LiveWindow.addSensor("Shooter", "Piston1 Reed Switch Back", self.piston1_reed_switch_back)
        wpilib.LiveWindow.addActuator("Shooter", "Latch Piston", self.latch_piston)
        super().__init__()

    def initDefaultCommand(self):
        """No default command."""
        pass

    def extend_both(self):
        """Extend both solenoids to shoot."""
        self.piston1.set(wpilib.DoubleSolenoid.Value.kForward)
        self.piston2.set(wpilib.DoubleSolenoid.Value.kForward)

    def retract_both(self):
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
        self.piston2.set(wpilib.DoubleSolenoid.Value.kForward)

    def retract2(self):
        """Retract solenoid 2 to prepare to shoot."""
        self.piston2.set(wpilib.DoubleSolenoid.Value.kReverse)

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
        self.latch_piston.set(True)

    def latch(self):
        """Latch so that pressure can build up and we aren't limited by air flow."""
        self.latch_piston.set(False)

    def toggle_latch_position(self):
        """Toggles the latch position"""
        self.latch_piston.set(not self.latch_piston.get())

    def piston1_is_extended(self):
        """:return Whether or not piston 1 is fully extended."""
        return not self.piston1_reed_switch_front.get()

    def piston1_is_retracted(self):
        """:return Whether or not piston 1 is fully retracted."""
        return not self.piston1_reed_switch_back.get()

    def off_both(self):
        """
        Turns off all double solenoids. Double solenoids hold their position when
        they are turned off. We should turn them off whenever possible to extend
        the life of the coils.
        """
        self.piston1.set(wpilib.DoubleSolenoid.Value.kOff)
        self.piston2.set(wpilib.DoubleSolenoid.Value.kOff)

    def goal_is_hot(self):
        """:return Whether or not the goal is hot as read by the banner sensor."""
        return self.hot_goal_sensor.get()
