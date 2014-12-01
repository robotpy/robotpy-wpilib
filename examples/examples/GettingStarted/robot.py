import wpilib


class MyRobot(wpilib.IterativeRobot):

    auto_loop_counter = 0

    def robotInit(self):
        """
        This function is called upon program startup and
        should be used for any initialization code.
        """
        self.robot_drive = wpilib.RobotDrive(0,1)
        self.stick = wpilib.Joystick(1)

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.auto_loop_counter = 0

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        #Check if we've completed 100 loops (approximately 2 seconds)
        if self.auto_loop_counter < 100:
            #Drive forwards at half speed
            self.robot_drive.drive(-0.5, 0)
            self.auto_loop_counter += 1
        else:
            #Stop robot
            self.robot_drive.drive(0, 0)

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.robot_drive.drive(self.stick)

    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()

if __name__ == "__main__":
    wpilib.run(MyRobot)
