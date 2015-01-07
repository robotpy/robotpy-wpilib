#!/usr/bin/env python3
'''
    This is a demo program showing the use of the CameraServer class.

    WARNING: While it may look like a good choice to use for your code if
    you're inexperienced, don't. Unless you know what you are doing, complex
    code will be much more difficult under this system. Use IterativeRobot
    or Command-Based instead if you're new.
'''

import wpilib

class MyRobot(wpilib.SampleRobot):

    def robotInit(self):
        camera = wpilib.USBCamera()
        camera.setExposureManual(50)
        camera.setBrightness(80)
        camera.updateSettings() # force update before we start thread

        server = wpilib.CameraServer.getInstance()
        server.startAutomaticCapture(camera)

    def operatorControl(self):
        while self.isOperatorControl() and self.isEnabled():
            wpilib.Timer.delay(0.02) # wait for a motor update time

if __name__ == '__main__':
    wpilib.run(MyRobot)
