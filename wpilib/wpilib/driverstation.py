# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.

import threading

import hal
import sys
import traceback

from .motorsafety import MotorSafety
from .timer import Timer

__all__ = ["DriverStation"]

class DriverStation:
    """Provide access to the network communication data to / from the Driver
    Station."""

    #: The number of joystick ports
    kJoystickPorts = 6
    
    #: Scaling factor from raw values to volts
    kDSAnalogInScaling = 5.0 / 1023.0
    lastEnabled = False

    class Alliance:
        """The robot alliance that the robot is a part of"""
        Red = 0
        Blue = 1
        Invalid = 2

    @staticmethod
    def getInstance():
        """Gets the global instance of the DriverStation

        :returns: DriverStation
        """
        if not hasattr(DriverStation, "instance"):
            DriverStation.instance = DriverStation()
        return DriverStation.instance

    def __init__(self):
        """DriverStation constructor.

        The single DriverStation instance is created statically with the
        instance static member variable.
        """
        self.mutex = threading.RLock()
        self.dataSem = threading.Condition(self.mutex)

        self.packetDataAvailableMutex = hal.initializeMutexNormal()
        self.packetDataAvailableSem = hal.initializeMultiWait()
        hal.HALSetNewDataSem(self.packetDataAvailableSem)

        self.controlWord = hal.HALControlWord()
        self.allianceStationID = -1
        self.joystickAxes = []
        self.joystickPOVs = []
        for i in range(self.kJoystickPorts):
            self.joystickAxes.append([0]*hal.kMaxJoystickAxes)
            self.joystickPOVs.append([0]*hal.kMaxJoystickPOVs)
        self.joystickButtons = [0]*self.kJoystickPorts

        self.approxMatchTimeOffset = -1.0
        self.userInDisabled = False
        self.userInAutonomous = False
        self.userInTeleop = False
        self.userInTest = False
        self.newControlData = False

        self.thread_keepalive = True

        self.thread = threading.Thread(target=self.task, name="FRCDriverStation")
        self.thread.daemon = True
        self.thread.start()

    def __del__(self):
        hal.deleteMultiWait(self.packetDataAvailableSem)
        hal.deleteMutex(self.packetDataAvailableMutex)

    def release(self):
        """Kill the thread"""
        self.thread_keepalive = False

    def task(self):
        """Provides the service routine for the DS polling thread."""
        safetyCounter = 0
        while self.thread_keepalive:
            hal.takeMultiWait(self.packetDataAvailableSem,
                              self.packetDataAvailableMutex, 0)
            with self.mutex:
                self.getData()
            with self.dataSem:
                self.dataSem.notify_all()
            safetyCounter += 1
            if safetyCounter >= 5:
                # print("Checking safety")
                MotorSafety.checkMotors()
                safetyCounter = 0
            if self.userInDisabled:
                hal.HALNetworkCommunicationObserveUserProgramDisabled()
            if self.userInAutonomous:
                hal.HALNetworkCommunicationObserveUserProgramAutonomous()
            if self.userInTeleop:
                hal.HALNetworkCommunicationObserveUserProgramTeleop()
            if self.userInTest:
                hal.HALNetworkCommunicationObserveUserProgramTest()

    def waitForData(self, timeout = None):
        """Wait for new data or for timeout, which ever comes first.  If
        timeout is None, wait for new data only.

        :param timeout: The maximum time in milliseconds to wait.
        """
        with self.dataSem:
            self.dataSem.wait(timeout)

    def getData(self):
        """Copy data from the DS task for the user.
        If no new data exists, it will just be returned, otherwise
        the data will be copied from the DS polling loop.
        """
        with self.mutex:
            # Get the status data
            self.controlWord = hal.HALGetControlWord()

            # Get the location/alliance data
            self.allianceStationID = hal.HALGetAllianceStation()

            # Get the status of all of the joysticks
            for stick in range(self.kJoystickPorts):
                self.joystickButtons[stick] = hal.HALGetJoystickButtons(stick)
                self.joystickAxes[stick] = hal.HALGetJoystickAxes(stick)
                self.joystickPOVs[stick] = hal.HALGetJoystickPOVs(stick)

            if not DriverStation.lastEnabled and self.isEnabled():
                # If starting teleop, assume that autonomous just took up 15 seconds
                if self.isAutonomous():
                    self.approxMatchTimeOffset = Timer.getFPGATimestamp()
                else:
                    self.approxMatchTimeOffset = Timer.getFPGATimestamp() - 15.0
            elif DriverStation.lastEnabled and not self.isEnabled():
                self.approxMatchTimeOffset = -1.0
            DriverStation.lastEnabled = self.isEnabled()

            self.newControlData = True

    def getBatteryVoltage(self):
        """Read the battery voltage.

        :returns: The battery voltage."""
        return hal.getVinVoltage()

    def getStickAxis(self, stick, axis):
        """Get the value of the axis on a joystick.
        This depends on the mapping of the joystick connected to the specified
        port.

        :param stick: The joystick to read.
        :param axis: The analog axis value to read from the joystick.
        :returns: The value of the axis on the joystick.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-5")

        if axis < 0 or axis >= hal.kMaxJoystickAxes:
            raise IndexError("Joystick axis is out of range")

        with self.mutex:
            if axis >= len(self.joystickAxes[stick]):
                self.reportError("WARNING: Joystick axis %d on port %d not available, check if controller is plugged in\n" % (axis, stick), False)
                return 0.0
            value = self.joystickAxes[stick][axis]

        if value < 0:
            return value / 128.0
        else:
            return value / 127.0

    def getStickPOV(self, stick, pov):
        """Get the state of a POV on the joystick.

        :param pov: which POV
        :returns: The angle of the POV in degrees, or -1 if the POV is not
                  pressed.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-5")

        if pov < 0 or pov >= hal.kMaxJoystickPOVs:
            raise IndexError("Joystick POV is out of range")

        with self.mutex:
            if pov >= len(self.joystickPOVs[stick]):
                self.reportError("WARNING: Joystick POV %d on port %d not available, check if controller is plugged in\n" % (pov, stick), False)
                return 0.0
            return self.joystickPOVs[stick][pov]

    def getStickButtons(self, stick):
        """The state of the buttons on the joystick.
        12 buttons (4 msb are unused) from the joystick.

        :param stick: The joystick to read.
        :returns: The state of the buttons on the joystick.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-3")

        with self.mutex:
            return self.joystickButtons[stick]

    def isEnabled(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be enabled.

        :returns: True if the robot is enabled, False otherwise.
        """
        with self.mutex:
            return self.controlWord.enabled != 0

    def isDisabled(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be disabled.

        :returns: True if the robot should be disabled, False otherwise.
        """
        return not self.isEnabled()

    def isAutonomous(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in autonomous mode.

        :returns: True if autonomous mode should be enabled, False otherwise.
        """
        with self.mutex:
            return self.controlWord.autonomous != 0

    def isTest(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in test mode.

        :returns: True if test mode should be enabled, False otherwise.
        """
        return self.controlWord.test != 0

    def isOperatorControl(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in operator-controlled mode.

        :returns: True if operator-controlled mode should be enabled,
            False otherwise.
        """
        with self.mutex:
            return not (self.controlWord.autonomous != 0 or
                        self.controlWord.test != 0)

    def isNewControlData(self):
        """Has a new control packet from the driver station arrived since the
        last time this function was called?

        :returns: True if the control data has been updated since the last
            call.
        """
        with self.mutex:
            result = self.newControlData
            self.newControlData = False
            return result

    def getAlliance(self):
        """Get the current alliance from the FMS.

        :returns: The current alliance
        :rtype: :class:`.Alliance`
        """
        with self.mutex:
            if self.allianceStationID in (hal.kHALAllianceStationID_red1,
                                          hal.kHALAllianceStationID_red2,
                                          hal.kHALAllianceStationID_red3):
                return self.Alliance.Red
            elif self.allianceStationID in (hal.kHALAllianceStationID_blue1,
                                            hal.kHALAllianceStationID_blue2,
                                            hal.kHALAllianceStationID_blue3):
                return self.Alliance.Blue
            else:
                return self.Alliance.Invalid

    def getLocation(self):
        """Gets the location of the team's driver station controls.

        :returns: The location of the team's driver station controls:
            1, 2, or 3
        """
        with self.mutex:
            if self.allianceStationID in (hal.kHALAllianceStationID_red1,
                                          hal.kHALAllianceStationID_blue1):
                return 1
            elif self.allianceStationID in (hal.kHALAllianceStationID_red2,
                                            hal.kHALAllianceStationID_blue2):
                return 2
            elif self.allianceStationID in (hal.kHALAllianceStationID_red3,
                                            hal.kHALAllianceStationID_blue3):
                return 3
            else:
                return 0

    def isFMSAttached(self):
        """Is the driver station attached to a Field Management System?

        :returns: True if the robot is competing on a field being controlled
            by a Field Management System
        """
        with self.mutex:
            return self.controlWord.fmsAttached != 0

    def getMatchTime(self):
        """Return the approximate match time.
        The FMS does not currently send the official match time to the robots.
        This returns the time since the enable signal sent from the Driver
        Station.
        
        * At the beginning of autonomous, the time is reset to 0.0 seconds.
        * At the beginning of teleop, the time is reset to +15.0 seconds.
        * If the robot is disabled, this returns 0.0 seconds.

        .. warning::

            This is not an official time (so it cannot be used to argue with
            referees).

        :returns: Match time in seconds since the beginning of autonomous
        """
        if self.approxMatchTimeOffset < 0.0:
            return 0.0
        return Timer.getFPGATimestamp() - self.approxMatchTimeOffset

    @staticmethod
    def reportError(error, printTrace):
        """Report error to Driver Station, and also prints error to `sys.stderr`. 
        Optionally appends stack trace to error message.
        
        :param printTrace: If True, append stack trace to error string
        """
        errorString = error
        if printTrace:
            exc = sys.exc_info()[0]
            stack = traceback.extract_stack()[:-1]  # last one is this func
            if exc is not None: # i.e. if an exception is present
                # remove call of full_stack, the printed exception
                # will contain the caught exception caller instead
                del stack[-1]
            trc = 'Traceback (most recent call last):\n'
            stackstr = trc + ''.join(traceback.format_list(stack))
            if exc is not None:
                 stackstr += '  ' + traceback.format_exc().lstrip(trc)
            errorString += ':\n' + stackstr
        #print(errorString, file=sys.stderr)
        hal.HALSetErrorData(errorString, 0)

    def InDisabled(self, entering):
        """Only to be used to tell the Driver Station what code you claim to
        be executing for diagnostic purposes only.

        :param entering: If True, starting disabled code; if False, leaving
            disabled code
        """
        self.userInDisabled = entering

    def InAutonomous(self, entering):
        """Only to be used to tell the Driver Station what code you claim to
        be executing for diagnostic purposes only.

        :param entering: If True, starting autonomous code; if False, leaving
            autonomous code
        """
        self.userInAutonomous = entering

    def InOperatorControl(self, entering):
        """Only to be used to tell the Driver Station what code you claim to
        be executing for diagnostic purposes only.

        :param entering: If True, starting teleop code; if False, leaving
            teleop code
        """
        self.userInTeleop = entering

    def InTest(self, entering):
        """Only to be used to tell the Driver Station what code you claim to
        be executing for diagnostic purposes only.

        :param entering: If True, starting test code; if False, leaving test
            code
        """
        self.userInTest = entering
