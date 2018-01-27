# validated: 2018-01-28 DV 48ae6c954a75 edu/wpi/first/wpilibj/DriverStation.java
# Copyright (c) 2008-2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.

import threading

import enum
import hal
import sys
import traceback

from networktables import NetworkTables

from .motorsafety import MotorSafety
from .timer import Timer

__all__ = ["DriverStation"]

import logging
logger = logging.getLogger('wpilib.ds')

JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL = 1.0


class MatchDataSender:
    def __init__(self):
        self.table = NetworkTables.getTable('FMSInfo')
        self.typeMetadata = self.table.getEntry('.type')
        self.typeMetadata.forceSetString('FMSInfo')
        self.gameSpecificMessage = self.table.getEntry('GameSpecificMessage')
        self.gameSpecificMessage.forceSetString('')
        self.eventName = self.table.getEntry('EventName')
        self.eventName.forceSetString('')
        self.matchNumber = self.table.getEntry('MatchNumber')
        self.matchNumber.forceSetDouble(0)
        self.replayNumber = self.table.getEntry('ReplayNumber')
        self.replayNumber.forceSetDouble(0)
        self.matchType = self.table.getEntry('MatchType')
        self.matchType.forceSetDouble(0)
        self.alliance = self.table.getEntry('IsRedAlliance')
        self.alliance.forceSetBoolean(True)
        self.station = self.table.getEntry('StationNumber')
        self.station.forceSetDouble(0)
        #self.controlWord = self.table.getEntry('FMSControlData')
        #self.controlWord.forceSetDouble(0)


class DriverStation:
    """Provide access to the network communication data to / from the Driver Station."""

    #: The number of joystick ports
    kJoystickPorts = 6

    _station_numbers = {
        hal.AllianceStationID.kBlue1: 1,
        hal.AllianceStationID.kBlue2: 2,
        hal.AllianceStationID.kBlue3: 3,
        hal.AllianceStationID.kRed1: 1,
        hal.AllianceStationID.kRed2: 2,
        hal.AllianceStationID.kRed3: 3,
    }

    class Alliance(enum.IntEnum):
        """The robot alliance that the robot is a part of."""
        Red = 0
        Blue = 1
        Invalid = 2

    class MatchType(enum.IntEnum):
        None_ = 0
        Practice = 1
        Qualification = 2
        Elimination = 3

    @classmethod
    def _reset(cls):
        ds = getattr(cls, 'instance', None)
        if ds is not None:
            ds.release()
            #hal.giveMultiWait(ds.packetDataAvailableSem)
            ds.thread.join()
            del cls.instance

    @classmethod
    def getInstance(cls):
        """Gets the global instance of the DriverStation.

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

        self.waitForDataCount = 0
        self.waitForDataCond = threading.Condition()

        self.cacheDataMutex = threading.RLock()

        self.joystickAxes = [hal.JoystickAxes() for _ in range(self.kJoystickPorts)]
        self.joystickPOVs = [hal.JoystickPOVs() for _ in range(self.kJoystickPorts)]
        self.joystickButtons = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]
        self.matchInfo = hal.MatchInfo(eventName=b'', gameSpecificMessage=b'')

        self.joystickButtonsPressed = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]
        self.joystickButtonsReleased = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]

        self.joystickAxesCache = [hal.JoystickAxes() for _ in range(self.kJoystickPorts)]
        self.joystickPOVsCache = [hal.JoystickPOVs() for _ in range(self.kJoystickPorts)]
        self.joystickButtonsCache = [hal.JoystickButtons() for _ in range(self.kJoystickPorts)]
        self.matchInfoCache = hal.MatchInfo(eventName=b'', gameSpecificMessage=b'')

        self.controlWordMutex = threading.RLock()
        self.controlWordCache = hal.ControlWord()
        self.lastControlWordUpdate = 0

        self.matchDataSender = MatchDataSender()

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
        """Kill the thread."""
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
        DriverStation._reportErrorImpl(False, 1, error, printTrace)

    @staticmethod
    def _reportErrorImpl(isError, code, error, printTrace):
        traceString = ""
        locString = ""

        if printTrace:
            exc = sys.exc_info()[0]
            stack = traceback.extract_stack()[:-2]  # last one is this func
            if exc is not None:  # i.e. if an exception is present
                # remove call of full_stack, the printed exception
                # will contain the caught exception caller instead
                del stack[-1]
                del stack[-1]

            locString = "%s.%s:%s" % (stack[-1][0], stack[-1][1], stack[-1][2])

            trc = 'Traceback (most recent call last):\n'
            stackstr = trc + ''.join(traceback.format_list(stack))
            if exc is not None:
                stackstr += '  ' + traceback.format_exc().lstrip(trc)
            traceString += ':\n' + stackstr
            logger.exception(error)
        elif isError:
            logger.error(error)
        else:
            logger.warning(error)

        hal.sendError(isError, code, False,
                      error.encode('utf-8'),
                      locString.encode('utf-8'),
                      traceString.encode('utf-8'), True)

    def getStickAxis(self, stick: int, axis: int) -> float:
        """Get the value of the axis on a joystick.

        This depends on the mapping of the joystick connected to the specified
        port.

        :param stick: The joystick port number
        :param axis: The analog axis value to read from the joystick.

        :returns: The value of the axis on the joystick.
        """
        if axis < 0 or axis >= hal.kMaxJoystickAxes:
            raise IndexError("Joystick axis is out of range")
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            joystickAxes = self.joystickAxes[stick]

            if axis >= joystickAxes.count:
                self._reportJoystickUnpluggedWarning("Joystick axis %d on port %d not available, check if controller is plugged in\n" % (axis, stick))
                return 0.0

            return joystickAxes.axes[axis]

    def getStickPOV(self, stick: int, pov: int) -> int:
        """Get the state of a POV on the joystick.

        :param stick: The joystick port number
        :param pov: which POV

        :returns: The angle of the POV in degrees, or -1 if the POV is not
                  pressed.
        """
        if pov < 0 or pov >= hal.kMaxJoystickPOVs:
            raise IndexError("Joystick POV is out of range")
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            joystickPOVs = self.joystickPOVs[stick]

            if pov >= joystickPOVs.count:
                self._reportJoystickUnpluggedWarning("Joystick POV %d on port %d not available, check if controller is plugged in\n" % (pov, stick))
                return -1
            return joystickPOVs.povs[pov]

    def getStickButtons(self, stick: int) -> int:
        """The state of all the buttons on the joystick.

        :param stick: The joystick port number

        :returns: The state of all buttons, as a bit array.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            return self.joystickButtons[stick].buttons

    def getStickButton(self, stick: int, button: int) -> bool:
        """The state of a button on the joystick. Button indexes begin at 1.

        :param stick: The joystick port number
        :param button: The button index, beginning at 1.

        :returns: The state of the button.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            joystickButtons = self.joystickButtons[stick]
            if button > joystickButtons.count:
                self._reportJoystickUnpluggedWarning("Joystick Button %d on port %d not available, check if controller is plugged in" % (button, stick))
                return False
            if button <= 0:
                self._reportJoystickUnpluggedError("Button indexes begin at 1 for WPILib")
                return False
            return ((0x1 << (button - 1)) & joystickButtons.buttons) != 0

    def getStickButtonPressed(self, stick: int, button: int) -> bool:
        """Whether one joystick button was pressed since the last check.
        Button indices begin at 1.

        :param stick: Joystick to read
        :param button: Button index, beginning at 1
        :returns: Whether the joystick button was pressed since the last check
        """
        if button <= 0:
            self._reportJoystickUnpluggedError("Button indexes begin at 1 for WPILib")
            return False
        if not 0 <= stick < self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        if self.joystickButtonsPressed[stick].buttons & 1 << (button - 1):
            self.joystickButtonsPressed[stick].buttons &= ~(1 << (button - 1))
            return True
        return False

    def getStickButtonReleased(self, stick: int, button: int) -> bool:
        """Whether one joystick button was released since the last check.
        Button indices begin at 1.

        :param stick: Joystick to read
        :param button: Button index, beginning at 1
        :returns: Whether the joystick button was released since the last check
        """
        if button <= 0:
            self._reportJoystickUnpluggedError("Button indexes begin at 1 for WPILib")
            return False
        if not 0 <= stick < self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        if self.joystickButtonsReleased[stick].buttons & 1 << (button - 1):
            self.joystickButtonsReleased[stick].buttons &= ~(1 << (button - 1))
            return True
        return False

    def getStickAxisCount(self, stick: int) -> int:
        """Returns the number of axes on a given joystick port.

        :param stick: The joystick port number

        :returns: The number of axes on the indicated joystick
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            return self.joystickAxes[stick].count

    def getStickPOVCount(self, stick: int) -> int:
        """Returns the number of POVs on a given joystick port.

        :param stick: The joystick port number

        :returns: The number of POVs on the indicated joystick
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            return self.joystickPOVs[stick].count

    def getStickButtonCount(self, stick: int) -> int:
        """Gets the number of buttons on a joystick.

        :param stick: The joystick port number

        :returns: The number of buttons on the indicated joystick.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            return self.joystickButtons[stick].count

    def getJoystickIsXbox(self, stick: int) -> bool:
        """Gets the value of isXbox on a joystick.

        :param stick: The joystick port number

        :returns: A boolean that returns the value of isXbox
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick]):
                self._reportJoystickUnpluggedWarning("WARNING: Joystick on port {} not avaliable, check if controller is "
                                                     "plugged in.\n".format(stick))
                return False

        return hal.getJoystickIsXbox(stick)

    def getJoystickType(self, stick: int) -> int:
        """
        Gets the value of type on a joystick

        :param stick: The joystick port number

        :returns: An integer that returns the value of type.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick]):
                self._reportJoystickUnpluggedWarning("Joystick on port {} not avaliable, check if controller is "
                                                     "plugged in.\n".format(stick))
                return -1

        return hal.getJoystickType(stick)

    def getJoystickName(self, stick: int) -> str:
        """
        Gets the name of a joystick

        :param stick: The joystick port number

        :returns: The joystick name.
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            # TODO: Remove this when calling for descriptor on empty stick no longer crashes.
            if 1 > self.joystickButtons[stick].count and 1 > len(self.joystickAxes[stick].axes):
                self._reportJoystickUnpluggedError("WARNING: Joystick on port {} not avaliable, check if controller is "
                                                   "plugged in.\n".format(stick))
                return ""

        return hal.getJoystickName(stick)

    def getJoystickAxisType(self, stick: int, axis: int) -> int:
        """Returns the types of Axes on a given joystick port.

        :param stick: The joystick port number
        :param axis: The target axis

        :returns: An integer that reports type of axis the axis is reporting to be
        """
        if stick < 0 or stick >= self.kJoystickPorts:
            raise IndexError("Joystick index is out of range, should be 0-%s" % self.kJoystickPorts)

        with self.cacheDataMutex:
            return hal.getJoystickAxisType(stick, axis)

    def isEnabled(self) -> bool:
        """Gets a value indicating whether the Driver Station requires the
        robot to be enabled.

        :returns: True if the robot is enabled, False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.enabled != 0 and self.controlWordCache.dsAttached != 0

    def isDisabled(self) -> bool:
        """Gets a value indicating whether the Driver Station requires the
        robot to be disabled.

        :returns: True if the robot should be disabled, False otherwise.
        """
        return not self.isEnabled()

    def isAutonomous(self) -> bool:
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in autonomous mode.

        :returns: True if autonomous mode should be enabled, False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.autonomous != 0

    def isOperatorControl(self) -> bool:
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in operator-controlled mode.

        :returns: True if operator-controlled mode should be enabled,
            False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return not (self.controlWordCache.autonomous != 0 or self.controlWordCache.test != 0)

    def isTest(self) -> bool:
        """Gets a value indicating whether the Driver Station requires the
        robot to be running in test mode.

        :returns: True if test mode should be enabled, False otherwise.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.test != 0

    def isDSAttached(self) -> bool:
        """Is the driver station attached to the robot?

        :returns: True if the robot is being controlled by a driver station.
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.dsAttached != 0

    def isNewControlData(self) -> bool:
        """Gets if a new control packet from the driver station arrived since
        the last time this function was called.

        :returns: True if the control data has been updated since the last
            call.
        """
        return hal.isNewControlData()

    def isFMSAttached(self) -> bool:
        """Gets if the driver station attached to a Field Management System.

        :returns: True if the robot is competing on a field being controlled
            by a Field Management System
        """
        with self.controlWordMutex:
            self._updateControlWord(False)
            return self.controlWordCache.fmsAttached != 0

    def isSysActive(self):
        """
        Gets a value indicating whether the FPGA outputs are enabled. The
        outputs may be disabled if the robot is disabled or e-stopped, the
        watchdog has expired, or if the roboRIO browns out.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.isSysActive`

        :returns: True if the FPGA outputs are enabled.
        """
        return hal.getSystemActive()

    def isBrownedOut(self):
        """
        Check if the system is browned out.

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.isBrownedOut`

        :returns: True if the system is browned out.
        """
        return hal.getBrownedOut()

    def getGameSpecificMessage(self) -> str:
        """Get the game specific message.

        :returns: The game specific message
        """
        with self.cacheDataMutex:
            return self.matchInfo.gameSpecificMessage.decode('utf-8')

    def getEventName(self) -> str:
        """Get the event name

        :returns: The event name
        """
        with self.cacheDataMutex:
            return self.matchInfo.eventName.decode('utf-8')

    def getMatchType(self) -> MatchType:
        """Get the match type.

        :returns: The match type
        """
        with self.cacheDataMutex:
            matchType = self.matchInfo.matchType

        return self.MatchType(matchType)

    def getMatchNumber(self) -> int:
        """Get the match number.

        :returns: The match number
        """
        with self.cacheDataMutex:
            return self.matchInfo.matchNumber

    def getReplayNumber(self) -> int:
        """Get the replay number.

        :returns: The replay number
        """
        with self.cacheDataMutex:
            return self.matchInfo.replayNumber

    def getAlliance(self) -> Alliance:
        """Get the current alliance from the FMS.

        :returns: The current alliance
        """
        allianceStationID = hal.getAllianceStation()
        hAid = hal.AllianceStationID

        if allianceStationID in (hAid.kRed1, hAid.kRed2, hAid.kRed3):
            return self.Alliance.Red
        elif allianceStationID in (hAid.kBlue1, hAid.kBlue2, hAid.kBlue3):
            return self.Alliance.Blue
        else:
            return self.Alliance.Invalid

    def getLocation(self) -> int:
        """Gets the location of the team's driver station controls.

        :returns: The location of the team's driver station controls:
            1, 2, or 3
        """
        allianceStationID = hal.getAllianceStation()
        return self._station_numbers.get(allianceStationID, 0)

    def waitForData(self, timeout: float = None) -> bool:
        """Wait for new data or for timeout, which ever comes first.

        If timeout is None, wait for new data only.

        :param timeout: The maximum time in seconds to wait.

        :returns: True if there is new data, otherwise False
        """
        with self.waitForDataCond:
            currentCount = self.waitForDataCount
            signaled = self.waitForDataCond.wait_for(lambda: self.waitForDataCount != currentCount, timeout)
            if not signaled:
                # Return False if a timeout happened
                return False
        return True

    def getMatchTime(self) -> int:
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

        .. deprecated:: 2018.0.0
            Use :meth:`.RobotController.getBatteryVoltage`

        :returns: The battery voltage in Volts.
        """
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

    def _sendMatchData(self):
        alliance = hal.getAllianceStation()
        hAid = hal.AllianceStationID
        isRedAlliance = alliance in {hAid.kRed1, hAid.kRed2, hAid.kRed3}
        stationNumber = self._station_numbers.get(alliance, 0)

        with self.cacheDataMutex:
            eventName = self.matchInfo.eventName.decode('utf-8')
            gameSpecificMessage = self.matchInfo.gameSpecificMessage.decode('utf-8')
            matchNumber = self.matchInfo.matchNumber
            replayNumber = self.matchInfo.replayNumber
            matchType = self.matchInfo.matchType

        self.matchDataSender.alliance.setBoolean(isRedAlliance)
        self.matchDataSender.station.setDouble(stationNumber)
        self.matchDataSender.eventName.setString(eventName)
        self.matchDataSender.gameSpecificMessage.setString(gameSpecificMessage)
        self.matchDataSender.matchNumber.setDouble(matchNumber)
        self.matchDataSender.replayNumber.setDouble(replayNumber)
        self.matchDataSender.matchType.setDouble(matchType)
        #self.matchDataSender.controlWord.setDouble(...)

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

        hal.getMatchInfo(self.matchInfoCache)

        # Force a control word update, to make sure the data is the newest.
        self._updateControlWord(True)

        # lock joystick mutex to swap cache data
        with self.cacheDataMutex:
            for i in range(self.kJoystickPorts):
                self.joystickButtonsPressed[i].buttons |= \
                    ~self.joystickButtons[i].buttons & self.joystickButtonsCache[i].buttons

                self.joystickButtonsReleased[i].buttons |= \
                    self.joystickButtons[i].buttons & ~self.joystickButtonsCache[i].buttons

            # move cache to actual data
            self.joystickAxes, self.joystickAxesCache = self.joystickAxesCache, self.joystickAxes
            self.joystickButtons, self.joystickButtonsCache = self.joystickButtonsCache, self.joystickButtons
            self.joystickPOVs, self.joystickPOVsCache = self.joystickPOVsCache, self.joystickPOVs

            self.matchInfo, self.matchInfoCache = self.matchInfoCache, self.matchInfo

        with self.waitForDataCond:
            self.waitForDataCount += 1
            self.waitForDataCond.notify_all()

        self._sendMatchData()

    def _reportJoystickUnpluggedError(self, message):
        """
        Reports errors related to unplugged joysticks and throttles them so that they don't overwhelm the DS.
        """
        currentTime = Timer.getFPGATimestamp()
        if currentTime > self.nextMessageTime:
            self.reportError(message, False)
            self.nextMessageTime = currentTime + JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL

    def _reportJoystickUnpluggedWarning(self, message):
        """
        Reports errors related to unplugged joysticks and throttles them so that they don't overwhelm the DS.
        """
        currentTime = Timer.getFPGATimestamp()
        if currentTime > self.nextMessageTime:
            self.reportWarning(message, False)
            self.nextMessageTime = currentTime + JOYSTICK_UNPLUGGED_MESSAGE_INTERVAL

    def _run(self):
        """Provides the service routine for the DS polling thread."""
        safetyCounter = 0

        while self.threadKeepAlive:
            hal.waitForDSData()
            self._getData()

            if self.isDisabled():
                safetyCounter = 0

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
        """Updates the data in the control word cache.

        Updates if the force parameter is set, or if 50ms have passed since the last update.

        :param force: True to force an update to the cache, otherwise update if 50ms have passed.
        """
        now = hal.getFPGATime()
        with self.controlWordMutex:
            if (now - self.lastControlWordUpdate) > 50 or force:
                hal.getControlWord(self.controlWordCache)
                self.lastControlWordUpdate = now
