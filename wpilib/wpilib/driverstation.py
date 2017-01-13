# validated: 2016-11-24 DS 1071686d8147 athena/java/edu/wpi/first/wpilibj/DriverStation.java
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

import logging
logger = logging.getLogger('wpilib.ds')

JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL = 1.0

class DriverStation:
    """Provide access to the network communication data to / from the Driver
    Station."""

    #: The number of joystick ports
    kJoystickPorts = 6

    class Alliance:
        """The robot alliance that the robot is a part of"""
        Red = 0
        Blue = 1
        Invalid = 2
        
    @staticmethod
    def _reset():
        if hasattr(DriverStation, 'instance'):
            ds = DriverStation.instance
            ds.release()
            #hal.giveMultiWait(ds.packetDataAvailableSem)
            ds.thread.join()
            del DriverStation.instance

    @classmethod
    def getInstance(cls):
        """Gets the global instance of the DriverStation

        :returns: :class:`DriverStation`
        """
        try:
            return cls.instance
        except AttributeError:
            cls.instance = None
            cls.instance = cls()
            return cls.instance

    def __init__(self):
        """DriverStation constructor.

        The single DriverStation instance is created statically with the
        instance static member variable, you should never create a
        DriverStation instance.
        """
        
        if not hasattr(DriverStation, 'instance') or DriverStation.instance is not None:
            raise ValueError("Do not create DriverStation instances, use DriverStation.getInstance() instead")
        
        # Java constructor vars
        
        self.mutex = threading.RLock()
        self.dataCond = threading.Condition(self.mutex)

        self.joystickMutex = threading.RLock()
        self.newControlData = False

        self.joystickAxes = [hal.JoystickAxes() for _ in range(self.kJoystickPorts)]
        self.joystickPOVs = [hal.JoystickPOVs() for _ in range(self.kJoystickPorts)]
        self.joystickButtons = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]
        
        self.joystickAxesCache = [hal.JoystickAxes() for _ in range(self.kJoystickPorts)]
        self.joystickPOVsCache = [hal.JoystickPOVs() for _ in range(self.kJoystickPorts)]
        self.joystickButtonsCache = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]
        
        self.controlWordMutex = threading.RLock()
        self.controlWordCache = hal.ControlWord()
        self.lastControlWordUpdate = 0
        
        # vars not initialized in constructor
        self.nextMessageTime = 0.0
        
        self.threadKeepAlive = True
        self.waitForDataPredicate = False
        
        self.userInDisabled = False
        self.userInAutonomous = False
        self.userInTeleop = False
        self.userInTest = False

        # Rest of constructor

        self.thread = threading.Thread(target=self._run, name="FRCDriverStation")
        self.thread.daemon = True
        self.thread.start()

    def release(self):
        """Kill the thread"""
        self.threadKeepAlive = False

    @staticmethod
    def reportError(error, printTrace):
        """Report error to Driver Station, and also prints error to `sys.stderr`.
        Optionally appends stack trace to error message.

        :param printTrace: If True, append stack trace to error string
        """
        DriverStation._reportErrorImpl(True, 1, error, printTrace)
        
    @staticmethod
    def reportWarning(error, printTrace):
        """Report warning to Driver Station, and also prints error to `sys.stderr`.
        Optionally appends stack trace to error message.

        :param printTrace: If True, append stack trace to warning string
        """
        DriverStation._reportErrorImpl(True, 1, error, printTrace)   
        
    @staticmethod
    def _reportErrorImpl(isError, code, error, printTrace):
        errorString = error
        traceString = ""
        locString = ""
        
        if printTrace:
            exc = sys.exc_info()[0]
            stack = traceback.extract_stack()[:-2]  # last one is this func
            if exc is not None: # i.e. if an exception is present
                # remove call of full_stack, the printed exception
                # will contain the caught exception caller instead
                del stack[-1]
                del stack[-1]
            
            locString = "%s.%s:%s" % (stack[-1][0], stack[-1][1], stack[-1][2])
                
            trc = 'Traceback (most recent call last):\n'
            stackstr = trc + ''.join(traceback.format_list(stack))
            if exc is not None:
                stackstr += '  ' + traceback.format_exc().lstrip(trc)
            errorString += ':\n' + stackstr
            
            logger.exception(error)
        else:
            logger.error(error)
        
        hal.sendError(isError, code, False,
                      error.encode('utf-8'),
                      locString.encode('utf-8'),
                      traceString.encode('utf-8'), True)
    
    def getStickAxis(self, stick, axis):
        """Get the value of the axis on a joystick.
        This depends on the mapping of the joystick connected to the specified
        port.

        :param stick: The joystick port number
        :type stick: int
        :param axis: The analog axis value to read from the joystick.
        :type axis: int
        
        :returns: The value of the axis on the joystick.
        """

        if axis < 0 or axis >= hal.kMaxJoystickAxes:
            raise IndexError("Joystick axis is out of range")
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            joystickAxes = self.joystickAxes[stick]

            if axis >= joystickAxes.count:
                self._reportJoystickUnpluggedWarning("Joystick axis %d on port %d not available, check if controller is plugged in\n" % (axis, stick))
                return 0.0
            
            return joystickAxes.axes[axis]

    def getStickPOV(self, stick, pov):
        """Get the state of a POV on the joystick.

        :param stick: The joystick port number
        :type stick: int
        :param pov: which POV
        :type pov: int
        
        :returns: The angle of the POV in degrees, or -1 if the POV is not
                  pressed.
        """
        if pov < 0 or pov >= hal.kMaxJoystickPOVs:
            raise IndexError("Joystick POV is out of range")
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            joystickPOVs = self.joystickPOVs[stick]

            if pov >= joystickPOVs.count:
                self._reportJoystickUnpluggedWarning("Joystick POV %d on port %d not available, check if controller is plugged in\n" % (pov, stick))
                return -1
            return joystickPOVs.povs[pov]

    def getStickButtons(self, stick):
        """The state of all the buttons on the joystick.

        :param stick: The joystick port number
        :type stick: int
        
        :returns: The state of all buttons, as a bit array.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            return self.joystickButtons[stick].buttons

    def getStickButton(self, stick, button):
        """The state of a button on the joystick. Button indexes begin at 1.

        :param stick: The joystick port number
        :type stick: int
        :param button: The button index, beginning at 1.
        :type button: int
        
        :returns: The state of the button.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            joystickButtons = self.joystickButtons[stick]
            if button > joystickButtons.count:
                self._reportJoystickUnpluggedWarning("Joystick Button %d on port %d not available, check if controller is plugged in" % (button, stick))
                return False
            if button <= 0:
                self._reportJoystickUnpluggedError("Button indexes begin at 1 for WPILib")
                return False
            return ((0x1 << (button - 1)) & joystickButtons.buttons) != 0

    def getStickAxisCount(self, stick):
        """Returns the number of axes on a given joystick port

        :param stick: The joystick port number
        :type stick: int

        :returns: The number of axes on the indicated joystick
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            return self.joystickAxes[stick].count
                

    def getStickPOVCount(self, stick):
        """Returns the number of POVs on a given joystick port

        :param stick: The joystick port number
        :type stick: int

        :returns: The number of POVs on the indicated joystick
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            return self.joystickPOVs[stick].count

    def getStickButtonCount(self, stick):
        """Gets the number of buttons on a joystick

        :param stick: The joystick port number
        :type stick: int

        :returns: The number of buttons on the indicated joystick.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            return self.joystickButtons[stick].count

    def getJoystickIsXbox(self, stick):
        """Gets the value of isXbox on a joystick

        :param stick: The joystick port number
        :type stick: int

        :returns A boolean that returns the value of isXbox
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)
        
        with self.joystickMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick]):
                self._reportJoystickUnpluggedWarning("WARNING: Joystick on port {} not avaliable, check if controller is "
                                                   "plugged in.\n".format(stick))
                return False
    
        return hal.getJoystickIsXbox(stick)

    def getJoystickType(self, stick):
        """
        Gets the value of type on a joystick

        :param stick: The joystick port number
        :type stick: int

        :returns An integer that returns the value of type.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)
        
        with self.joystickMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick]):
                self._reportJoystickUnpluggedWarning("Joystick on port {} not avaliable, check if controller is "
                                                     "plugged in.\n".format(stick))
                return -1
    
        return hal.getJoystickType(stick)

    def getJoystickName(self, stick):
        """
        Gets the name of a joystick

        :param stick: The joystick port number
        :type stick: int

        :returns The joystick name.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.joystickMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick]):
                self._reportJoystickUnpluggedError("WARNING: Joystick on port {} not avaliable, check if controller is "
                                                   "plugged in.\n".format(stick))
                return ""

        return hal.getJoystickName(stick)

    def getJoystickAxisType(self, stick, axis):
        """Returns the types of Axes on a given joystick port.

        :param stick: The joystick port number
        :type stick: int
        :param axis: The target axis
        :type axis: int

        :returns An integer that reports type of axis the axis is reporting to be
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)
        
        with self.joystickMutex:
            return hal.getJoystickAxisType(stick, axis)

    def isEnabled(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be enabled.

        :returns: True if the robot is enabled, False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.enabled != 0 and self.controlWordCache.dsAttached != 0

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
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.autonomous != 0

    def isOperatorControl(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in operator-controlled mode.

        :returns: True if operator-controlled mode should be enabled,
            False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return not (self.controlWordCache.autonomous != 0 or self.controlWordCache.test != 0)

    def isTest(self):
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in test mode.

        :returns: True if test mode should be enabled, False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.test != 0
    
    def isDSAttached(self):
        """Is the driver station attached to the robot?

        :returns: True if the robot is being controlled by a driver station.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.dsAttached != 0
    
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
    
    def isFMSAttached(self):
        """Is the driver station attached to a Field Management System?

        :returns: True if the robot is competing on a field being controlled
            by a Field Management System
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.fmsAttached != 0
    
    def isSysActive(self):
        """
        Gets a value indicating whether the FPGA outputs are enabled. The outputs may be disabled
        if the robot is disabled or e-stopped, the watdhog has expired, or if the roboRIO browns out.

        :returns: True if the FPGA outputs are enabled.
        """
        return hal.getSystemActive()
    
    def isBrownedOut(self):
        """
        Check if the system is browned out.

        :returns: True if the system is browned out.
        """
        return hal.getBrownedOut()
    
    def getAlliance(self):
        """Get the current alliance from the FMS.

        :returns: The current alliance
        :rtype: :class:`DriverStation.Alliance`
        """
        allianceStationID = hal.getAllianceStation()
        hAid = hal.AllianceStationID
        
        if allianceStationID in (hAid.kRed1, hAid.kRed2, hAid.kRed3):
            return self.Alliance.Red
        elif allianceStationID in (hAid.kBlue1, hAid.kBlue2, hAid.kBlue3):
            return self.Alliance.Blue
        else:
            return self.Alliance.Invalid
    
    def getLocation(self):
        """Gets the location of the team's driver station controls.

        :returns: The location of the team's driver station controls:
            1, 2, or 3
        """
        allianceStationID = hal.getAllianceStation()
        hAid = hal.AllianceStationID
        
        if allianceStationID in (hAid.kRed1, hAid.kBlue1):
            return 1
        elif allianceStationID in (hAid.kRed2, hAid.kBlue2):
            return 2
        elif allianceStationID in (hAid.kRed3, hAid.kBlue3):
            return 3
        else:
            return 0
    
    def waitForData(self, timeout = None):
        """Wait for new data or for timeout, which ever comes first.  If
        timeout is None, wait for new data only.

        :param timeout: The maximum time in seconds to wait.
        
        :returns: True if there is new data, otherwise False
        """
        with self.dataCond:
            return self.dataCond.wait_for(self._waitForDataPredicateFn, timeout)
            
    def _waitForDataPredicateFn(self):
        retval = self.waitForDataPredicate
        self.waitForDataPredicate = False
        return retval

    def getMatchTime(self):
        """Return the approximate match time.
        The FMS does not currently send the official match time to the robots, but
        does send an approximate match time. The value will count down the time
        remaining in the current period (auto or teleop).

        .. warning::

            This is not an official time (so it cannot be used to argue with
            referees or guarantee that a function will trigger before a match ends).

        The Practice Match function of the DS approximates the behaviour seen on the field.

        :returns: Time remaining in current match period (auto or teleop) in seconds
        """
        return hal.getMatchTime()

    def getBatteryVoltage(self):
        """Read the battery voltage.

        :returns: The battery voltage in Volts."""
        return hal.getVinVoltage()

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

    def _getData(self):
        """Copy data from the DS task for the user.
        If no new data exists, it will just be returned, otherwise
        the data will be copied from the DS polling loop.
        """
        
        # Get the status of all of the joysticks
        for stick in range(self.kJoystickPorts):
            hal.getJoystickAxes(stick, self.joystickAxesCache[stick])
            hal.getJoystickPOVs(stick, self.joystickPOVsCache[stick])
            hal.getJoystickButtons(stick, self.joystickButtonsCache[stick])
        
        # Force a control word update, to make sure the data is the newest.
        self._updateControlWord(True)
        
        # lock joystick mutex to swap cache data
        with self.joystickMutex:
            
            # move cache to actual data
            self.joystickAxes, self.joystickAxesCache = self.joystickAxesCache, self.joystickAxes
            self.joystickButtons, self.joystickButtonsCache = self.joystickButtonsCache, self.joystickButtons
            self.joystickPOVs, self.joystickPOVsCache = self.joystickPOVsCache, self.joystickPOVs
        
    def _reportJoystickUnpluggedError(self, message):
        """
        Reports errors related to unplugged joysticks and throttles them so that they don't overwhelm the DS
        """
        currentTime = Timer.getFPGATimestamp()
        if currentTime > self.nextMessageTime:
            self.reportError(message, False)
            self.nextMessageTime = currentTime + JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL

    def _reportJoystickUnpluggedWarning(self, message):
        """
        Reports errors related to unplugged joysticks and throttles them so that they don't overwhelm the DS
        """
        currentTime = Timer.getFPGATimestamp()
        if currentTime > self.nextMessageTime:
            self.reportError(message, False)
            self.nextMessageTime = currentTime + JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL

    def _run(self):
        """Provides the service routine for the DS polling thread."""
        safetyCounter = 0
        
        while self.threadKeepAlive:
            hal.waitForDSData()
            self._getData()
            
            with self.dataCond:
                self.waitForDataPredicate = True
                self.dataCond.notify_all()
            
            #with self.mutex: # dataCond already holds the mutex
                self.newControlData = True
            
            safetyCounter += 1
            if safetyCounter >= 4:
                MotorSafety.checkMotors()
                safetyCounter = 0
                
            if self.userInDisabled:
                hal.observeUserProgramDisabled()
                
            if self.userInAutonomous:
                hal.observeUserProgramAutonomous()
                
            if self.userInTeleop:
                hal.observeUserProgramTeleop()
                
            if self.userInTest:
                hal.observeUserProgramTest()
    
    def _updateControlWord(self, force):
        """Updates the data in the control word cache. Updates if the force parameter is set, or if
        50ms have passed since the last update.
        
        :param force: True to force an update to the cache, otherwise update if 50ms have passed.
        """
        now = hal.getFPGATime()
        with self.controlWordMutex:
            if now - self.lastControlWordUpdate > 50 or force:
                hal.getControlWord(self.controlWordCache)
                self.lastControlWordUpdate = now
        
