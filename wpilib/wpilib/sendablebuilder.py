# validated: 2019-01-04 TW 97ba195b881e edu/wpi/first/wpilibj/smartdashboard/SendableBuilderImpl.java
# ----------------------------------------------------------------------------
# Copyright (c) 2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------
from typing import Callable, Any, List, Optional
from networktables import NetworkTables
from networktables.entry import NetworkTableEntry
from networktables.networktable import NetworkTable

__all__ = ["SendableBuilder"]


class Property:
    def __init__(
        self,
        table: NetworkTable,
        key: str,
        update: Callable,
        setter: Callable,
        listen_local: bool,
    ) -> None:
        self.entry = table.getEntry(key)
        self.key = key
        self.update = update
        self.setter = setter
        self.listener = None
        # python-specific: sendable chooser needs to be able to hear local updates
        self.listen_local = listen_local

    def createListener(self, entry: NetworkTableEntry) -> None:
        flags = (
            NetworkTables.NotifyFlags.IMMEDIATE
            | NetworkTables.NotifyFlags.NEW
            | NetworkTables.NotifyFlags.UPDATE
        )
        if self.listen_local:
            flags |= NetworkTables.NotifyFlags.LOCAL
        self.listener = entry.addListener(
            lambda entry, key, value, param: self.setter(value), flags
        )

    def startListener(self) -> None:
        if self.listener is None and self.setter is not None:
            self.createListener(self.entry)

    def stopListener(self) -> None:
        if self.listener is not None:
            self.entry.removeListener(self.listener)
            self.listener = None


class SendableBuilder:
    def __init__(self) -> None:
        self.table = None
        self._updateTable = None
        self.safeState = None
        self.properties = []
        self.controllableEntry = None
        self.actuator = False

    def setTable(self, table: NetworkTable) -> None:
        """
        Set the network table.  Must be called prior to any Add* functions being called.

        :param table: Network table
        """
        self.table = table
        self.controllableEntry = table.getEntry(".controllable")

    def getTable(self) -> NetworkTable:
        """
        Get the network table.

        :returns: The network table
        """
        return self.table

    def isActuator(self) -> bool:
        """
        Return whether this sendable should be treated as an actuator.
        """
        return self.actuator

    def updateTable(self) -> None:
        """
        Update the network table values by calling the getters for all properties.
        """
        for prop in self.properties:
            if prop.update is not None:
                prop.update(prop.entry)

        if self._updateTable is not None:
            self._updateTable()

    def startListeners(self) -> None:
        """Hook setters for all properties"""
        for prop in self.properties:
            prop.startListener()
        if self.controllableEntry is not None:
            self.controllableEntry.setBoolean(True)

    def stopListeners(self) -> None:
        """Unhook setters for all properties"""
        for prop in self.properties:
            prop.stopListener()
        if self.controllableEntry is not None:
            self.controllableEntry.setBoolean(False)

    def startLiveWindowMode(self) -> None:
        """
        Start LiveWindow mode by hooking the setters for all properties. Also calls
        the safeState function if one was provided.
        """
        if self.safeState is not None:
            self.safeState()

        self.startListeners()

    def stopLiveWindowMode(self) -> None:
        """
        Stop LiveWindow mode by unhooking the setters for all properties. Also calls
        the safeState function if one was provided.
        """
        self.stopListeners()
        if self.safeState is not None:
            self.safeState()

    def setSmartDashboardType(self, type: str) -> None:
        """
        Set the string representation of the named data type that will be used
        by the smart dashboard for this sendable.
   
        :param type: data type
        """
        self.table.getEntry(".type").setString(type)

    def setActuator(self, value) -> None:
        """
        Set a flag indicating if this sendable should be treated as an actuator.
        By default this flag is false.

        :param value: true if actuator, false if not
        """
        self.table.getEntry(".actuator").setBoolean(value)
        self.actuator = value

    def setSafeState(self, func: Callable) -> None:
        """
        Set the function that should be called to set the Sendable into a safe
        state.  This is called when entering and exiting Live Window mode.

        :param func:    function
        """
        self.safeState = func

    def setUpdateTable(self, func: Callable) -> None:
        """
        Set the function that should be called to update the network table
        for things other than properties.  Note this function is not passed
        the network table object; instead it should use the entry handles
        returned by getEntry().

        :param func:    function
        """
        self._updateTable = func

    def getEntry(self, key: str) -> NetworkTableEntry:
        """
        Add a property without getters or setters.  This can be used to get
        entry handles for the function called by setUpdateTable().

        :param key:   property name
        :returns: Network table entry
        """
        return self.table.getEntry(key)

    def _addProperty(
        self, key: str, updater: Callable, setter: Callable, listen_local: bool
    ) -> None:
        prop = Property(self.table, key, updater, setter, listen_local)
        self.properties.append(prop)

    def addBooleanProperty(
        self,
        key: str,
        getter: Optional[Callable[[], bool]],
        setter: Optional[Callable[[bool], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a boolean property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = None if getter is None else lambda entry: entry.setBoolean(getter())
        self._addProperty(key, updater, setter, local)

    def addDoubleProperty(
        self,
        key: str,
        getter: Optional[Callable[[], float]],
        setter: Optional[Callable[[float], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a double property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = None if getter is None else lambda entry: entry.setDouble(getter())
        self._addProperty(key, updater, setter, local)

    def addStringProperty(
        self,
        key: str,
        getter: Optional[Callable[[], str]],
        setter: Optional[Callable[[str], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a string property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = None if getter is None else lambda entry: entry.setString(getter())
        self._addProperty(key, updater, setter, local)

    def addBooleanArrayProperty(
        self,
        key: str,
        getter: Optional[Callable[[], List[bool]]],
        setter: Optional[Callable[[List[bool]], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a boolean array property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = (
            None if getter is None else lambda entry: entry.setBooleanArray(getter())
        )
        self._addProperty(key, updater, setter, local)

    def addDoubleArrayProperty(
        self,
        key: str,
        getter: Optional[Callable[[], List[float]]],
        setter: Optional[Callable[[List[float]], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a double array property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = (
            None if getter is None else lambda entry: entry.setDoubleArray(getter())
        )
        self._addProperty(key, updater, setter, local)

    def addStringArrayProperty(
        self,
        key: str,
        getter: Optional[Callable[[], List[str]]],
        setter: Optional[Callable[[List[str]], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a string array property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = (
            None if getter is None else lambda entry: entry.setStringArray(getter())
        )
        self._addProperty(key, updater, setter, local)

    def addRawProperty(
        self,
        key: str,
        getter: Optional[Callable[[], bytes]],
        setter: Optional[Callable[[bytes], Any]],
        local: bool = False,
    ) -> None:
        """
        Add a raw property.
   
        :param key:     property name
        :param getter:  getter function (returns current value)
        :param setter:  setter function (sets new value)
        :param local:   (python-specific) if True, setter will be called on local updates
        """
        updater = None if getter is None else lambda entry: entry.setRaw(getter())
        self._addProperty(key, updater, setter, local)
