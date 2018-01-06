# validated: 2018-01-06 DS ee33296e1fe6 edu/wpi/first/wpilibj/smartdashboard/SmartDashboard.java

# validation note: 2017-10-22: Not using the getEntry() stuff that Java uses,
#                              as using the existing table stuff is more
#                              efficient

#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import threading
from ._impl.utils import match_arglist, HasAttribute
from .sendablebuilder import SendableBuilder

__all__ = ["SmartDashboard"]


class Data:
    def __init__(self, sendable):
        self.sendable = sendable
        self.builder = SendableBuilder()


class SmartDashboard:
    """The bridge between robot programs and the SmartDashboard on the laptop

    When a value is put into the SmartDashboard, it pops up on the
    SmartDashboard on the remote host. Users can put values into and get values
    from the SmartDashboard.
    
    These values can also be accessed by a NetworkTables client via the
    'SmartDashboard' table::
    
        from networktables import NetworkTables
        sd = NetworkTables.getTable('SmartDashboard')
        
        # sd.putXXX and sd.getXXX work as expected here
    
    """
    # The NetworkTable used by SmartDashboard
    table = None
    # A table linking tables in the SmartDashboard to the SmartDashboardData
    # objects they came from.
    tablesToData = {}
    mutex = threading.RLock()

    @classmethod
    def _reset(cls):
        cls.tablesToData = {}
        cls.table = None

    @classmethod
    def getTable(cls):
        if cls.table is None:
            from networktables import NetworkTables
            cls.table = NetworkTables.getTable("SmartDashboard")
            hal.report(hal.UsageReporting.kResourceType_SmartDashboard,
                       hal.UsageReporting.kSmartDashboard_Instance)
        return cls.table

    @classmethod
    def putData(cls, *args, **kwargs):
        """
        Maps the specified key (name of the :class:`.Sendable` if not provided) 
        to the specified value in this table.
        The value can be retrieved by calling the get method with a key that
        is equal to the original key.

        Two argument formats are supported: 
        
        - key, data
        - value
        
        :param key: the key (cannot be None)
        :type  key: str
        :param data: the value
        :type data: :class:`.Sendable`
        :param value: the value
        :type value: :class:`.Sendable`
        """
        with cls.mutex:
            key_arg = ("key", [str])
            data_arg = ("data", [HasAttribute("initSendable")])
            value_arg = ("value", [HasAttribute("initSendable")])
            templates = [[key_arg, data_arg],
                         [value_arg],]

            index, results = match_arglist('SmartDashboard.putData',
                                       args, kwargs, templates)
            if index == 0:
                key = results['key']
                data = results["data"]
            elif index == 1:
                data = results["value"]
                key = data.getName()
            else:
                raise ValueError("only (key, data) or (value) accepted")

            sddata = cls.tablesToData.get(key, None)
            if sddata is None or sddata.sendable != data:
                if sddata is not None:
                    sddata.builder.stopListeners()

                sddata = Data(data)
                cls.tablesToData[key] = sddata
                dataTable = cls.getTable().getSubTable(key)
                sddata.builder.setTable(dataTable)
                data.initSendable(sddata.builder)
                sddata.builder.updateTable()
                sddata.builder.startListeners()
                dataTable.getEntry('.name').setString(key)

    @classmethod
    def getData(cls, key):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        
        :returns: the value
        
        :raises: :exc:`KeyError` if the key doesn't exist
        """
        data = cls.tablesToData.get(subtable, None)
        if data is None:
            raise KeyError("SmartDashboard data does not exist: '%s'" % key)
        return data.sendable
    
    @classmethod
    def getEntry(cls, key):
        """Gets the entry for the specified key.
        
        :param key: the key name
        :rtype: :class:`.NetworkTableEntry`
        """
        table = cls.getTable()
        return table.getEntry(key)

    @classmethod
    def containsKey(cls, key):
        """Checks the table and tells if it contains the specified key.

        :param key: key the key to search for
        
        :returns: true if the table as a value assigned to the given key
        """
        table = cls.getTable()
        return table.containsKey(key)

    @classmethod
    def getKeys(cls, types=0):
        """Get the keys stored in the SmartDashboard table of NetworkTables.

        :param types: bitmask of types; 0 is treated as a "don't care".
        
        :returns: keys currently in the table
        """
        table = cls.getTable()
        return table.getKeys(types)

    @classmethod
    def setPersistent(cls, key):
        """Makes a key's value persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        """
        table = cls.getTable()
        table.setPersistent(key)

    @classmethod
    def clearPersistent(cls, key):
        """Stop making a key's value persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        """
        table = cls.getTable()
        table.clearPersistent(key)

    @classmethod
    def isPersistent(cls, key):
        """Returns whether the value is persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        
        :returns: True if the value is persistent.
        """
        table = cls.getTable()
        return table.isPersistent(key)

    @classmethod
    def setFlags(cls, key, flags):
        """Sets flags on the specified key in this table. The key can
        not be null.

        :param key: the key name
        :param flags: the flags to set (bitmask)
        """
        table = cls.getTable()
        table.setFlags(key, flags)

    @classmethod
    def clearFlags(cls, key, flags):
        """Clears flags on the specified key in this table. The key can
        not be null.

        :param key: the key name
        :param flags: the flags to clear (bitmask)
        """
        table = cls.getTable()
        table.clearFlags(key, flags)

    @classmethod
    def getFlags(cls, key):
        """ Returns the flags for the specified key.

        :param key: the key name
        
        :returns: the flags, or 0 if the key is not defined
        """
        table = cls.getTable()
        return table.getFlags(key)

    @classmethod
    def delete(cls, key):
        """Deletes the specified key in this table. The key can
        not be null.

        :param key: the key name
        """
        table = cls.getTable()
        table.delete(key)

    @classmethod
    def putBoolean(cls, key, value):
        """Put a boolean in the table.

        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :return False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putBoolean(key, value)

    @classmethod
    def setDefaultBoolean(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultBoolean(key, defaultValue)

    @classmethod
    def getBoolean(cls, key, defaultValue):
        """Returns the boolean the key maps to. If the key does not exist or is of
        different type, it will return the default value.
        
        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getBoolean(key, defaultValue)

    @classmethod
    def putNumber(cls, key, value):
        """Put a number in the table.
        
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :returns: False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putNumber(key, value)

    @classmethod
    def setDefaultNumber(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultNumber(key, defaultValue)

    @classmethod
    def getNumber(cls, key, defaultValue):
        """Returns the number the key maps to. If the key does not exist or is of
        different type, it will return the default value.
        
        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getNumber(key, defaultValue)

    @classmethod
    def putString(cls, key, value):
        """Put a string in the table.
        
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :returns: False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putString(key, value)

    @classmethod
    def setDefaultString(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultString(key, defaultValue)

    @classmethod
    def getString(cls, key, defaultValue):
        """Returns the string the key maps to. If the key does not exist or is of
        different type, it will return the default value.
        
        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getString(key, defaultValue)

    @classmethod
    def putBooleanArray(cls, key, value):
        """Put a boolean array in the table.
        
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :returns: False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putBooleanArray(key, value)

    @classmethod
    def setDefaultBooleanArray(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultBooleanArray(key, defaultValue)

    @classmethod
    def getBooleanArray(cls, key, defaultValue):
        """Returns the boolean array the key maps to. If the key does not exist or is of
        different type, it will return the default value.
        
        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getBooleanArray(key, defaultValue)

    @classmethod
    def putNumberArray(cls, key, value):
        """Put a number array in the table.
        
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :returns: False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putNumberArray(key, value)

    @classmethod
    def setDefaultNumberArray(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultNumberArray(key, defaultValue)

    @classmethod
    def getNumberArray(cls, key, defaultValue):
        """Returns the number array the key maps to. If the key does not exist or is of
        different type, it will return the default value.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getNumberArray(key, defaultValue)
    
    @classmethod
    def putStringArray(cls, key, value):
        """Put a string array in the table
        
        :param key: the key to be assigned to
        :type key: str
        :param value: the value that will be assigned
        :type value: list(str)
        
        :returns: False if the table key already exists with a different type
        :rtype: bool
        """
        table = cls.getTable()
        return table.putStringArray(key, value)
    
    @classmethod
    def setDefaultStringArray(cls, key, defaultValue):
        """If the key doesn't currently exist, then the specified value will
        be assigned to the key.
        
        :param key: the key to be assigned to
        :type key: str
        :param defaultValue: the default value to set if key doesn't exist.
        :type defaultValue: list(str)
        
        :returns: False if the table key exists with a different type
        :rtype: bool
        """
        table = cls.getTable()
        return table.setDefaultStringArray(key, defaultValue)
    
    @classmethod
    def getStringArray(cls, key, defaultValue):
        """Returns the string array the key maps to. If the key does not exist or is
        of different type, it will return the default value.
        
        :param key: the key to look up
        :type key: str
        :param defaultValue: the value to be returned if no value is found
        :type defaultValue: list(str)
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        :rtype: list(str)
        """
        table = cls.getTable()
        return table.getStringArray(key, defaultValue)

    @classmethod
    def putRaw(cls, key, value):
        """Put a raw value (byte array) in the table.
        
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        
        :returns: False if the table key already exists with a different type
        """
        table = cls.getTable()
        return table.putRaw(key, value)

    @classmethod
    def setDefaultRaw(cls, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        
        :returns: False if the table key exists with a different type
        """
        table = cls.getTable()
        return table.setDefaultRaw(key, defaultValue)

    @classmethod
    def getRaw(cls, key, defaultValue):
        """Returns the raw value (byte array) the key maps to. If the key does not exist or is of
        different type, it will return the default value.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        """
        table = cls.getTable()
        return table.getRaw(key, defaultValue)

    @classmethod
    def updateValues(cls):
        with cls.mutex:
            for data in cls.tablesToData.values():
                data.builder.updateTable()
