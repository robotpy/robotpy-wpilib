
from wpilib.buttons import Trigger

class DoubleButton(Trigger):
    """
    A custom button that is triggered when two buttons on a Joystick are
    simultaneously pressed.
    """

    def __init__(self, joy, button1, button2):
        self.joy = joy
        self.button1 = button1
        self.button2 = button2

    def get(self):
        return self.joy.getRawButton(self.button1) and self.joy.getRawButton(self.button2)
