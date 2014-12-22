
import wpilib

from wpilib import SmartDashboard
from wpilib.buttons import JoystickButton

from commands.autonomous import Autonomous
from commands.close_claw import CloseClaw
from commands.drive_straight import DriveStraight
from commands.open_claw import OpenClaw
from commands.pickup import Pickup
from commands.place import Place
from commands.prepare_to_pickup import PrepareToPickup
from commands.set_distance_to_box import SetDistanceToBox
from commands.set_elevator_setpoint import SetElevatorSetpoint
from commands.set_wrist_setpoint import SetWristSetpoint

class OI:
    
    def __init__(self, robot):
        
        self.joy = wpilib.Joystick(0)
        
        # Put Some buttons on the SmartDashboard
        SmartDashboard.putData("Elevator Bottom", SetElevatorSetpoint(robot, 0));
        SmartDashboard.putData("Elevator Platform", SetElevatorSetpoint(robot, 0.2));
        SmartDashboard.putData("Elevator Top", SetElevatorSetpoint(robot, 0.3));
        
        SmartDashboard.putData("Wrist Horizontal", SetWristSetpoint(robot, 0));
        SmartDashboard.putData("Raise Wrist", SetWristSetpoint(robot, -45));
        
        SmartDashboard.putData("Open Claw", OpenClaw(robot));
        SmartDashboard.putData("Close Claw", CloseClaw(robot));
        
        SmartDashboard.putData("Deliver Soda", Autonomous(robot));
        
        # Create some buttons
        d_up = JoystickButton(self.joy, 5)
        d_right = JoystickButton(self.joy, 6)
        d_down = JoystickButton(self.joy, 7)
        d_left = JoystickButton(self.joy, 8)
        l2 = JoystickButton(self.joy, 9)
        r2 = JoystickButton(self.joy, 10)
        l1 = JoystickButton(self.joy, 11)
        r1 = JoystickButton(self.joy, 12)

        # Connect the buttons to commands
        d_up.whenPressed(SetElevatorSetpoint(robot, 0.2))
        d_down.whenPressed(SetElevatorSetpoint(robot, -0.2))
        d_right.whenPressed(CloseClaw(robot))
        d_left.whenPressed(OpenClaw(robot))
        
        r1.whenPressed(PrepareToPickup(robot))
        r2.whenPressed(Pickup(robot))
        l1.whenPressed(Place(robot))
        l2.whenPressed(Autonomous(robot))
    
    def getJoystick(self):
        return self.joy
        