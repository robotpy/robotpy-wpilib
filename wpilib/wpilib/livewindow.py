# validated: 2015-12-24 DS 6d854af shared/java/edu/wpi/first/wpilibj/livewindow/LiveWindow.java

from networktables import NetworkTable
from .command import Scheduler

import logging
logger = logging.getLogger(__name__)

__all__ = ["LiveWindow"]

class _LiveWindowComponent:
    """A LiveWindow component is a device (sensor or actuator) that should be
    added to the SmartDashboard in test mode. The components are cached until
    the first time the robot enters Test mode. This allows the components to
    be inserted, then renamed."""
    def __init__(self, subsystem, name, isSensor):
        self.subsystem = subsystem
        self.name = str(name)
        self.isSensor = isSensor

class LiveWindow:
    """The public interface for putting sensors and
    actuators on the LiveWindow."""

    sensors = set()
    #actuators = set()
    components = {}
    livewindowTable = None
    statusTable = None
    liveWindowEnabled = False
    firstTime = True
    
    @staticmethod
    def _reset():
        LiveWindow.sensors = set()
        LiveWindow.components = {}
        LiveWindow.livewindowTable = None
        LiveWindow.statusTable = None
        LiveWindow.liveWindowEnabled = False
        LiveWindow.firstTime = True

    @staticmethod
    def initializeLiveWindowComponents():
        """Initialize all the LiveWindow elements the first time we enter
        LiveWindow mode. By holding off creating the NetworkTable entries, it
        allows them to be redefined before the first time in LiveWindow mode.
        This allows default sensor and actuator values to be created that are
        replaced with the custom names from users calling addActuator and
        addSensor.
        """
        logger.info("Initializing the components first time")
        LiveWindow.livewindowTable = NetworkTable.getTable("LiveWindow")
        LiveWindow.statusTable = LiveWindow.livewindowTable.getSubTable("~STATUS~")
        for component, c in LiveWindow.components.items():
            logger.info("Initializing table for '%s' '%s'" % (c.subsystem, c.name))
            LiveWindow.livewindowTable.getSubTable(c.subsystem).putString("~TYPE~", "LW Subsystem")
            table = LiveWindow.livewindowTable.getSubTable(c.subsystem).getSubTable(c.name)
            table.putString("~TYPE~", component.getSmartDashboardType())
            table.putString("Name", c.name)
            table.putString("Subsystem", c.subsystem)
            component.initTable(table)
            if c.isSensor:
                LiveWindow.sensors.add(component)

    @staticmethod
    def setEnabled(enabled):
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
        if LiveWindow.liveWindowEnabled != enabled:
            if enabled:
                logger.info("Starting live window mode.")
                if LiveWindow.firstTime:
                    LiveWindow.initializeLiveWindowComponents()
                    LiveWindow.firstTime = False
                Scheduler.getInstance().disable()
                Scheduler.getInstance().removeAll()
                bad_components = []
                for component in LiveWindow.components.keys():
                    try:
                        component.startLiveWindowMode()
                    except Exception as e:
                        logger.error("Exception running startLiveWindowMode() on {}, removing from component list.".format(component))
                        logger.exception(e)
                        bad_components.append(component)
                for component in bad_components:
                    del(LiveWindow.components[component])
            else:
                logger.info("Stopping live window mode.")
                for component in LiveWindow.components.keys():
                    component.stopLiveWindowMode()
                Scheduler.getInstance().enable()
            LiveWindow.liveWindowEnabled = enabled
            LiveWindow.statusTable.putBoolean("LW Enabled", enabled)

    @staticmethod
    def run():
        """The run method is called repeatedly to keep the values refreshed
        on the screen in test mode.
        """
        LiveWindow.updateValues()

    @staticmethod
    def addSensor(subsystem, name, component):
        """Add a Sensor associated with the subsystem and with call it by the
        given name.

        :param subsystem: The subsystem this component is part of.
        :param name: The name of this component.
        :param component: A LiveWindowSendable component that represents a
            sensor.
        """
        LiveWindow.components[component] = \
                _LiveWindowComponent(subsystem, name, True)
        LiveWindow.sensors.add(component)

    @staticmethod
    def addActuator(subsystem, name, component):
        """Add an Actuator associated with the subsystem and with call it by
        the given name.

        :param subsystem: The subsystem this component is part of.
        :param name: The name of this component.
        :param component: A LiveWindowSendable component that represents a
            actuator.
        """
        LiveWindow.components[component] = \
                _LiveWindowComponent(subsystem, name, False)

    @staticmethod
    def updateValues():
        """Puts all sensor values on the live window."""
        # TODO: gross - needs to be sped up
        for lws in LiveWindow.sensors:
            lws.updateTable()
        # TODO: Add actuators?
        # TODO: Add better rate limiting.

    @staticmethod
    def addSensorChannel(moduleType, channel, component):
        """Add Sensor to LiveWindow. The components are shown with the type
        and channel like this: Gyro[0] for a gyro object connected to the
        first analog channel.

        :param moduleType: A string indicating the type of the module used in
            the naming (above)
        :param channel: The channel number the device is connected to
        :param component: A reference to the object being added
        """
        LiveWindow.addSensor("Ungrouped", "%s[%s]" % (moduleType, channel),
                             component)

    @staticmethod
    def addActuatorChannel(moduleType, channel, component):
        """Add Actuator to LiveWindow. The components are shown with the
        module type, slot and channel like this: Servo[0,2] for a servo
        object connected to the first digital module and PWM port 2.

        :param moduleType: A string that defines the module name in the label
            for the value
        :param channel: The channel number the device is plugged into
            (usually PWM)
        :param component: The reference to the object being added
        """
        LiveWindow.addActuator("Ungrouped", "%s[%s]" % (moduleType, channel),
                               component)

    @staticmethod
    def addActuatorModuleChannel(moduleType, moduleNumber, channel, component):
        """Add Actuator to LiveWindow. The components are shown with the
        module type, slot and channel like this: Servo[0,2] for a servo
        object connected to the first digital module and PWM port 2.

        :param moduleType: A string that defines the module name in the label
            for the value
        :param moduleNumber: The number of the particular module type
        :param channel: The channel number the device is plugged into
            (usually PWM)
        :param component: The reference to the object being added
        """
        LiveWindow.addActuator(
                "Ungrouped",
                "%s[%s,%s]" % (moduleType, moduleNumber, channel),
                component)

    @staticmethod
    def removeComponent(component):
        """Removes a component from LiveWindow.

        :param component: The reference to the object being removed.
        """
        if component in LiveWindow.components:
            if LiveWindow.components[component].isSensor:
                LiveWindow.sensors.remove(component)
            del(LiveWindow.components[component])
