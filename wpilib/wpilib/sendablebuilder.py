# validated: 2018-01-01 EN 40eb6dfc9b83 edu/wpi/first/wpilibj/smartdashboard/SendableBuilderImpl.java
#----------------------------------------------------------------------------
# Copyright (c) 2017 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------
from networktables import NetworkTables


__all__ = ['SendableBuilder']


class Property:
    def __init__(self, table, key, update, setter):
        self.entry = table.getEntry(key)
        self.key = key
        self.update = update
        self.setter = setter
        self.listener = None

    def createListener(self, entry):
        self.listener = entry.addListener(lambda entry, key, value, param: self.setter(value),
            NetworkTables.NotifyFlags.IMMEDIATE |
            NetworkTables.NotifyFlags.NEW |
            NetworkTables.NotifyFlags.UPDATE)
    
    def startListener(self):
        if self.listener is None and self.setter is not None:
            self.createListener(self.entry)

    def stopListener(self):
        if self.listener is not None:
            self.entry.removeListener(self.listener)
            self.listener = None
        

class SendableBuilder:
    def __init__(self):
        self.table = None
        self._updateTable = None
        self.safeState = None
        self.properties = []

    def setTable(self, table): 
        """
        Set the network table.  Must be called prior to any Add* functions being called.

        :param table: Network table
        :type table: :class:`networktables.networktable.NetworkTable`
        """
        self.table = table

    def getTable(self):
        """
        Get the network table.

        :returns: The network table
        :rtype: :class:`networktables.networktable.NetworkTable`
        """
        return self.table

    def updateTable(self):
        """
        Update the network table values by calling the getters for all properties.
        """
        for prop in self.properties:
            if prop.update is not None:
                prop.update(prop.entry)

        if self._updateTable is not None:
            self._updateTable()

    def startListeners(self):
        """Hook setters for all properties"""
        for prop in self.properties:
            prop.startListener()

    def stopListeners(self):
        """Unhook setters for all properties"""
        for prop in self.properties:
            prop.stopListener()

    def startLiveWindowMode(self):
        """
        Start LiveWindow mode by hooking the setters for all properties. Also calls
        the safeState function if one was provided.
        """
        if self.safeState is not None:
            self.safeState()

        self.startListeners()

    def stopLiveWindowMode(self):
        """
        Stop LiveWindow mode by unhooking the setters for all properties. Also calls
        the safeState function if one was provided.
        """
        self.stopListeners()
        if self.safeState is not None:
            self.safeState()

    def setSmartDashboardType(self, type):
        """
        Set the string representation of the named data type that will be used
        by the smart dashboard for this sendable.
   
        :param type: data type
        :type type: str
        """
        self.table.getEntry(".type").setString(type)

    def setSafeState(self, func):
        """
        Set the function that should be called to set the Sendable into a safe
        state.  This is called when entering and exiting Live Window mode.

        :param func:    function
        """
        self.safeState = func

    def setUpdateTable(self, func):
        """
        Set the function that should be called to update the network table
        for things other than properties.  Note this function is not passed
        the network table object; instead it should use the entry handles
        returned by getEntry().

        :param func:    function
        """
        self._updateTable = func

    def getEntry(self, key):
        """
        Add a property without getters or setters.  This can be used to get
        entry handles for the function called by setUpdateTable().

        :param key:   property name
        :type key: str
        :returns: Network table entry
        :rtype: :class:`networktables.entry.NetworkTableEntry`
        """
        return self.table.getEntry(key)

    def _addProperty(self, key, updater, setter):
        prop = Property(self.table, key, updater, setter)
        self.properties.append(prop)

    def addBooleanProperty(self, key, getter, setter):
        """
        Add a boolean property.
   
        :param key:     property name
        :type getter: str
        :param getter:  getter function (returns current value)
        :type getter: () -> bool
        :param setter:  setter function (sets new value)
        :type setter: (bool) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setBoolean(getter())
        self._addProperty(key, updater, setter)

    def addDoubleProperty(self, key, getter, setter):
        """
        Add a double property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> float
        :param setter:  setter function (sets new value)
        :type setter: (float) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setDouble(getter())
        self._addProperty(key, updater, setter)

    def addStringProperty(self, key, getter, setter):
        """
        Add a string property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> str
        :param setter:  setter function (sets new value)
        :type setter: (str) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setString(getter())
        self._addProperty(key, updater, setter)

    def addBooleanArrayProperty(self, key, getter, setter):
        """
        Add a boolean array property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> bool[]
        :param setter:  setter function (sets new value)
        :type setter: (bool[]) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setBooleanArray(getter())
        self._addProperty(key, updater, setter)

    def addDoubleArrayProperty(self, key, getter, setter):
        """
        Add a double array property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> float[]
        :param setter:  setter function (sets new value)
        :type setter: (float[]) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setDoubleArray(getter())
        self._addProperty(key, updater, setter)

    def addStringArrayProperty(self, key, getter, setter):
        """
        Add a string array property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> str[]
        :param setter:  setter function (sets new value)
        :type setter: (str[]) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setStringArray(getter())
        self._addProperty(key, updater, setter)

    def addRawProperty(self, key, getter, setter):
        """
        Add a raw property.
   
        :param key:     property name
        :type key: str
        :param getter:  getter function (returns current value)
        :type getter: () -> bytes
        :param setter:  setter function (sets new value)
        :type setter: (bytes) -> Any
        """
        updater = None if getter is None else lambda entry: entry.setRaw(getter())
        self._addProperty(key, updater, setter)
