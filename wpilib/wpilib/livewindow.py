# validated: 2019-01-02 DV 97ba195b881e edu/wpi/first/wpilibj/livewindow/LiveWindow.java
# ----------------------------------------------------------------------------
#  Copyright (c) 2008-2017 FIRST. All Rights Reserved.
#  Open Source Software - may be modified and shared by FRC teams. The code
#  must be accompanied by the FIRST BSD license file in the root directory of
#  the project.
# ----------------------------------------------------------------------------
import logging
import threading
import warnings
from typing import Optional, Union

from networktables import NetworkTablesInstance
from networktables.entry import NetworkTableEntry
from networktables.networktable import NetworkTable
from .sendable import Sendable
from .sendablebuilder import SendableBuilder


logger = logging.getLogger(__name__)

__all__ = ["LiveWindow"]


class Component:
    def __init__(self, sendable: Sendable, parent: Optional[Sendable]) -> None:
        self.sendable = sendable
        self.parent = parent
        self.builder = SendableBuilder()
        self.firstTime = True
        self.telemetryEnabled = True


class _LiveWindowComponent:
    """A LiveWindow component is a device (sensor or actuator) that should be
    added to the SmartDashboard in test mode. The components are cached until
    the first time the robot enters Test mode. This allows the components to
    be inserted, then renamed."""

    def __init__(self, subsystem, name: str, isSensor: bool) -> None:
        self.subsystem = subsystem
        self.name = str(name)
        self.isSensor = isSensor


class LiveWindow:
    """The public interface for putting sensors and
    actuators on the LiveWindow."""

    components = {}
    _liveWindowTable = None
    _statusTable = None
    _enabledEntry = None
    startLiveWindow = False
    liveWindowEnabled = False
    telemetryEnabled = True
    mutex = threading.RLock()

    @classmethod
    def liveWindowTable(cls) -> NetworkTable:
        if cls._liveWindowTable is None:
            cls._liveWindowTable = NetworkTablesInstance.getDefault().getTable(
                "LiveWindow"
            )
        return cls._liveWindowTable

    @classmethod
    def statusTable(cls) -> NetworkTable:
        if cls._statusTable is None:
            cls._statusTable = cls.liveWindowTable().getSubTable(".status")
        return cls._statusTable

    @classmethod
    def enabledEntry(cls) -> NetworkTableEntry:
        if cls._enabledEntry is None:
            cls._enabledEntry = cls.statusTable().getEntry("LW Enabled")
        return cls._enabledEntry

    @classmethod
    def _reset(cls) -> None:
        cls.components = {}
        cls._liveWindowTable = None
        cls._statusTable = None
        cls._enabledEntry = None
        cls.startLiveWindow = False
        cls.liveWindowEnabled = False
        cls.telemetryEnabled = True

    @classmethod
    def isEnabled(cls) -> bool:
        return cls.liveWindowEnabled

    @classmethod
    def setEnabled(cls, enabled: bool) -> None:
        """Set the enabled state of LiveWindow. If it's being enabled, turn
        off the scheduler and remove all the commands from the queue and
        enable all the components registered for LiveWindow. If it's being
        disabled, stop all the registered components and reenable the
        scheduler.

        TODO: add code to disable PID loops when enabling LiveWindow. The
        commands should reenable the PID loops themselves when they get
        rescheduled. This prevents arms from starting to move around, etc.
        after a period of adjusting them in LiveWindow mode.
        """
        from .command import Scheduler

        with cls.mutex:
            if cls.liveWindowEnabled != enabled:
                cls.startLiveWindow = enabled
                cls.liveWindowEnabled = enabled
                cls.updateValues()  # Force table generation now to make sure everything is defined
                scheduler = Scheduler.getInstance()
                if enabled:
                    logger.info("Starting live window mode.")
                    scheduler.disable()
                    scheduler.removeAll()
                else:
                    logger.info("Stopping live window mode.")
                    components = list(cls.components.values())
                    for component in components:
                        component.builder.stopLiveWindowMode()
                    scheduler.enable()
                cls.enabledEntry().setBoolean(enabled)

    @classmethod
    def run(cls) -> None:
        """The run method is called repeatedly to keep the values refreshed
        on the screen in test mode.

        .. deprecated:: 2018.0.0
            No longer required
        """
        warnings.warn(
            "run is deprecated. It is no longer required.",
            DeprecationWarning,
            stacklevel=2,
        )
        cls.updateValues()

    @classmethod
    def addSensor(
        cls, subsystem: str, name: Union[str, int], component: Sendable
    ) -> None:
        """Add a Sensor associated with the subsystem and with call it by the
        given name.

        :param subsystem: The subsystem this component is part of.
        :param name: The name of this component.
        :param component: A LiveWindowSendable component that represents a
            sensor.

        .. deprecated:: 2018.0.0
            Use :meth:`.Sendable.setName` instead.
        """
        warnings.warn(
            "addSensor is deprecated. "
            + "Use Sendable.setName(subsystem, name) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        with cls.mutex:
            cls.add(component)
            component.setName(subsystem, name)

    @classmethod
    def addActuator(cls, subsystem: str, name: str, component: Sendable) -> None:
        """Add an Actuator associated with the subsystem and with call it by
        the given name.

        :param subsystem: The subsystem this component is part of.
        :param name: The name of this component.
        :param component: A LiveWindowSendable component that represents a actuator.

        .. deprecated:: 2018.0.0
            Use :meth:`.Sendable.setName` instead.
        """
        warnings.warn(
            "addActuator is deprecated. "
            + "Use Sendable.setName(subsystem, name) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        with cls.mutex:
            cls.add(component)
            component.setName(subsystem, name)

    @classmethod
    def addSensorChannel(
        cls, moduleType: str, channel: int, component: Sendable
    ) -> None:
        """Add Sensor to LiveWindow. The components are shown with the type
        and channel like this: Gyro[0] for a gyro object connected to the
        first analog channel.

        :param moduleType: A string indicating the type of the module used in
            the naming (above)
        :param channel: The channel number the device is connected to
        :param component: A reference to the object being added

        .. deprecated:: 2018.0.0
            Use :meth:`.SendableBase.setName` instead.
        """
        warnings.warn(
            "addSensorChannel is deprecated. "
            + "Use SendableBase.setName(moduleType, channel) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        cls.add(component)
        component.setName("Ungrouped", "%s[%s]" % (moduleType, channel))

    @classmethod
    def addActuatorChannel(
        cls, moduleType: str, channel: int, component: Sendable
    ) -> None:
        """Add Actuator to LiveWindow. The components are shown with the
        module type, slot and channel like this: Servo[0,2] for a servo
        object connected to the first digital module and PWM port 2.

        :param moduleType: A string that defines the module name in the label
            for the value
        :param channel: The channel number the device is plugged into
            (usually PWM)
        :param component: The reference to the object being added

        .. deprecated:: 2018.0.0
            Use :meth:`.SendableBase.setName` instead.
        """
        warnings.warn(
            "addActuatorChannel is deprecated. "
            + "Use SendableBase.setName(moduleType, channel) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        cls.add(component)
        component.setName("Ungrouped", "%s[%s]" % (moduleType, channel))

    @classmethod
    def addActuatorModuleChannel(
        cls, moduleType: str, moduleNumber: int, channel: int, component: Sendable
    ) -> None:
        """Add Actuator to LiveWindow. The components are shown with the
        module type, slot and channel like this: Servo[0,2] for a servo
        object connected to the first digital module and PWM port 2.

        :param moduleType: A string that defines the module name in the label
            for the value
        :param moduleNumber: The number of the particular module type
        :param channel: The channel number the device is plugged into
            (usually PWM)
        :param component: The reference to the object being added

        .. deprecated:: 2018.0.0
            Use :meth:`.SendableBase.setName` instead.
        """
        warnings.warn(
            "addActuatorModuleChannel is deprecated. "
            + "Use SendableBase.setName(moduleType, moduleNumber, channel) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        cls.add(component)
        component.setName(
            "Ungrouped", "%s[%s,%s]" % (moduleType, moduleNumber, channel)
        )

    @classmethod
    def add(cls, sendable: Sendable) -> None:
        """
        Add a component to the LiveWindow.

        :param sendable: component to add
        """
        with cls.mutex:
            if sendable not in cls.components:
                cls.components[sendable] = Component(sendable, None)

    @classmethod
    def addChild(cls, parent: Sendable, child: object) -> None:
        """
        Add a child component to a component.

        :param parent: parent component
        :param child: child component
        """
        with cls.mutex:
            component = cls.components.get(child, None)
            if component is None:
                component = Component(None, parent)
                cls.components[child] = component
            else:
                component.parent = parent
            component.telemetryEnabled = False

    @classmethod
    def remove(cls, sendable: Sendable) -> None:
        """
        Remove a component from the LiveWindow.

        :param sendable: component to remove
        """
        with cls.mutex:
            if sendable in cls.components:
                component = cls.components[sendable]
                del cls.components[sendable]
                if cls.isEnabled():
                    component.builder.stopLiveWindowMode()

    @classmethod
    def enableTelemetry(cls, sendable: Sendable) -> None:
        """
        Enable telemetry for a single component.

        :param sendable: component
        """
        with cls.mutex:
            cls.telemetryEnabled = True
            component = cls.components.get(sendable, None)
            if component is not None:
                component.telemetryEnabled = True

    @classmethod
    def disableTelemetry(cls, sendable: Sendable) -> None:
        """
        Disable telemetry for a single component.  

        :param sendable: component
        """
        with cls.mutex:
            component = cls.components.get(sendable, None)
            if component is not None:
                component.telemetryEnabled = False

    @classmethod
    def disableAllTelemetry(cls) -> None:
        """ Disable ALL telemetry """
        with cls.mutex:
            cls.telemetryEnabled = False
            for component in cls.components.values():
                component.telemetryEnabled = False

    @classmethod
    def updateValues(cls) -> None:
        with cls.mutex:
            # only do this if either LiveWindow mode or telemetry is enabled
            if not cls.liveWindowEnabled and not cls.telemetryEnabled:
                return

            components = list(cls.components.values())
            for component in components:
                if (
                    component.sendable is not None
                    and component.parent is None
                    and (cls.liveWindowEnabled or component.telemetryEnabled)
                ):
                    if component.firstTime:
                        # By holding off creating the NetworkTable entries, it allows the
                        # components to be redefined. This allows default sensor and actuator
                        # values to be created that are replaced with the custom names from
                        # users calling setName.
                        name = component.sendable.getName()
                        if name == "":
                            continue
                        subsystem = component.sendable.getSubsystem()
                        ssTable = cls.liveWindowTable().getSubTable(subsystem)
                        if name == subsystem:
                            table = ssTable
                        else:
                            table = ssTable.getSubTable(name)
                        table.getEntry(".name").setString(name)
                        component.builder.setTable(table)
                        component.sendable.initSendable(component.builder)
                        ssTable.getEntry(".type").setString("LW Subsystem")

                        component.firstTime = False

                    if cls.startLiveWindow:
                        component.builder.startLiveWindowMode()
                    component.builder.updateTable()

            cls.startLiveWindow = False
