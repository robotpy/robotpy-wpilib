
import math

import wpilib
from wpilib.command import Subsystem

from commands.tankdrive_with_joystick import TankDriveWithJoystick


class DriveTrain(Subsystem):
    '''The DriveTrain subsystem incorporates the sensors and actuators attached to
       the robots chassis. These include four drive motors, a left and right encoder
       and a gyro.
    '''

    def __init__(self, robot):
        super().__init__()
        self.robot = robot

        self.front_left_motor = wpilib.Talon(1)
        self.back_left_motor = wpilib.Talon(2)
        self.front_right_motor = wpilib.Talon(3)
        self.back_right_motor = wpilib.Talon(4)

        self.drive = wpilib.RobotDrive(self.front_left_motor,
                                       self.back_left_motor,
                                       self.front_right_motor,
                                       self.back_right_motor)

        self.left_encoder = wpilib.Encoder(1, 2)
        self.right_encoder = wpilib.Encoder(3, 4)

        # Encoders may measure differently in the real world and in
        # simulation. In this example the robot moves 0.042 barleycorns
        # per tick in the real world, but the simulated encoders
        # simulate 360 tick encoders. This if statement allows for the
        # real robot to handle this difference in devices.
        if robot.isReal():
            self.left_encoder.setDistancePerPulse(0.042)
            self.right_encoder.setDistancePerPulse(0.042)
        else:
            # Circumference in ft = 4in/12(in/ft)*PI
            self.left_encoder.setDistancePerPulse((4.0/12.0*math.pi) / 360.0)
            self.right_encoder.setDistancePerPulse((4.0/12.0*math.pi) / 360.0)

        self.rangefinder = wpilib.AnalogInput(6)
        self.gyro = wpilib.AnalogGyro(1)

        wpilib.LiveWindow.addActuator("Drive Train", "Front_Left Motor", self.front_left_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Back Left Motor", self.back_left_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Front Right Motor", self.front_right_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Back Right Motor", self.back_right_motor)
        wpilib.LiveWindow.addSensor("Drive Train", "Left Encoder", self.left_encoder)
        wpilib.LiveWindow.addSensor("Drive Train", "Right Encoder", self.right_encoder)
        wpilib.LiveWindow.addSensor("Drive Train", "Rangefinder", self.rangefinder)
        wpilib.LiveWindow.addSensor("Drive Train", "Gyro", self.gyro)

    def initDefaultCommand(self):
        '''When no other command is running let the operator drive around
           using the PS3 joystick'''
        self.setDefaultCommand(TankDriveWithJoystick(self.robot))

    def log(self):
        '''The log method puts interesting information to the SmartDashboard.'''
        wpilib.SmartDashboard.putNumber("Left Distance", self.left_encoder.getDistance())
        wpilib.SmartDashboard.putNumber("Right Distance", self.right_encoder.getDistance())
        wpilib.SmartDashboard.putNumber("Left Speed", self.left_encoder.getRate())
        wpilib.SmartDashboard.putNumber("Right Speed", self.right_encoder.getRate())
        wpilib.SmartDashboard.putNumber("Gyro", self.gyro.getAngle())

    def driveManual(self, left, right):
        ''' Tank style driving for the DriveTrain. 
            
            :param left: Speed in range [-1, 1]
            :param right: Speed in range [-1, 1]
        '''
        self.drive.tankDrive(left, right)

    def driveJoystick(self, joy):
        ''':param joy: The ps3 style joystick to use to drive tank style'''
        self.driveManual(-joy.getY(), -joy.getAxis(wpilib.Joystick.AxisType.kThrottle))

    def getHeading(self):
        ''' :returns: The robots heading in degrees'''
        return self.gyro.getAngle()

    def reset(self):
        '''Reset the robots sensors to the zero states'''
        self.gyro.reset()
        self.left_encoder.reset()
        self.right_encoder.reset()

    def getDistance(self):
        ''' :returns: The distance driven (average of left and right encoders)'''
        return (self.left_encoder.getDistance() + self.right_encoder.getDistance()) / 2.0

    def getDistanceToObstacle(self):
        ''' :returns: The distance to the obstacle detected by the rangefinder'''
        
        # Really meters in simulation since it's a rangefinder...
        return self.rangefinder.getAverageVoltage()
