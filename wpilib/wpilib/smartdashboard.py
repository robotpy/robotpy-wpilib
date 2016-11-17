# validated: 2016-11-17 AA 64ebe7f shared/java/edu/wpi/first/wpilibj/smartdashboard/SmartDashboard.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal

__all__ = ["SmartDashboard"]

class SmartDashboard:
    """The bridge between robot programs and the SmartDashboard on the laptop

    When a value is put into the SmartDashboard, it pops up on the
    SmartDashboard on the remote host. Users can put values into and get values
    from the SmartDashboard.
    
    These values can also be accessed by a NetworkTables client via the
    'SmartDashboard' table::
    
        from networktables import NetworkTable
        sd = NetworkTable.getTable('SmartDashboard')
        
        # sd.putXXX and sd.getXXX work as expected here
    
    """
    # The NetworkTable used by SmartDashboard
    table = None
    # A table linking tables in the SmartDashboard to the SmartDashboardData
    # objects they came from.
    tablesToData = {}

    class _defaultValueSentry:
        pass
    
    @staticmethod
    def _reset():
        SmartDashboard.tablesToData = {}
        SmartDashboard.table = None

    @staticmethod
    def getTable():
        if SmartDashboard.table is None:
            from networktables import NetworkTable
            SmartDashboard.table = NetworkTable.getTable("SmartDashboard")
            hal.HALReport(hal.HALUsageReporting.kResourceType_SmartDashboard,
                          hal.HALUsageReporting.kSmartDashboard_Instance)
        return SmartDashboard.table

    @staticmethod
    def putData(*args, **kwargs):
        """Maps the specified key to the specified value in this table.
        The value can be retrieved by calling the get method with a key that
        is equal to the original key.

        Two argument formats are supported: key, data:
        
        :param key: the key (cannot be None)
        :type  key: str
        :param data: the value

        Or the single argument "value":
        
        :param value: the named value (getName is called to retrieve the value)
        """
        # NOTE: mix of args and kwargs not allowed
        if kwargs and not args:
            if "value" in kwargs:
                data = kwargs["value"]
                key = data.getName()
            else:
                key = kwargs["key"]
                data = kwargs["data"]
        elif len(args) == 1 and not kwargs:
            data = args[0]
            key = data.getName()
        elif len(args) == 2 and not kwargs:
            key, data = args
        else:
            raise ValueError("only key, data or value accepted")

        table = SmartDashboard.getTable()
        dataTable = table.getSubTable(key)
        dataTable.putString("~TYPE~", data.getSmartDashboardType())
        data.initTable(dataTable)
        SmartDashboard.tablesToData[dataTable] = data

    @staticmethod
    def getData(key):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        :returns: the value
        
        :raises: :exc:`KeyError` if the key doesn't exist
        """
        table = SmartDashboard.getTable()
        subtable = table.getSubTable(key)
        data = SmartDashboard.tablesToData.get(subtable)
        if data is None:
            raise KeyError("SmartDashboard data does not exist: '%s'" % key)
        return data

    @staticmethod
    def containsKey(key):
        """Checks the table and tells if it contains the specified key.

        :param key: key the key to search for
        :return: true if the table as a value assigned to the given key
        """
        table = SmartDashboard.getTable()
        return table.containsKey(key)

    @staticmethod
    def getKeys(types=0):
        """Get array of keys in the table.

        :param types: bitmask of types; 0 is treated as a "don't care".
        :return: keys currently in the table
        """
        table = SmartDashboard.getTable()
        return table.getKeys(types)

    @staticmethod
    def setPersistent(key):
        """Makes a key's value persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        """
        table = SmartDashboard.getTable()
        table.setPersistent(key)

    @staticmethod
    def clearPersistent(key):
        """Stop making a key's value persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        """
        table = SmartDashboard.getTable()
        table.clearPersistent(key)

    @staticmethod
    def isPersistent(key):
        """Returns whether the value is persistent through program restarts.
        The key cannot be null.

        :param key: the key name
        :return: True if the value is persistent.
        """
        table = SmartDashboard.getTable()
        return table.isPersistent(key)

    @staticmethod
    def setFlags(key, flags):
        """Sets flags on the specified key in this table. The key can
        not be null.

        :param key: the key name
        :param flags: the flags to set (bitmask)
        """
        table = SmartDashboard.getTable()
        table.setFlags(key, flags)

    @staticmethod
    def clearFlags(key, flags):
        """Clears flags on the specified key in this table. The key can
        not be null.

        :param key: the key name
        :param flags: the flags to clear (bitmask)
        """
        table = SmartDashboard.getTable()
        table.clearFlags()

    @staticmethod
    def getFlags(key):
        """ Returns the flags for the specified key.

        :param key: the key name
        :return: the flags, or 0 if the key is not defined
        """
        table = SmartDashboard.getTable()
        return table.getFlags(key)

    @staticmethod
    def delete(key):
        """Deletes the specified key in this table. The key can
        not be null.

        :param key: the key name
        """
        table = SmartDashboard.getTable()
        table.delete(key)

    @staticmethod
    def putBoolean(key, value):
        """Put a boolean in the table.

        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :return False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putBoolean(key, value)

    @staticmethod
    def setDefaultBoolean(key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultBoolean(key, defaultValue)

    @staticmethod
    def getBoolean(key, defaultValue=_defaultValueSentry):
        """Returns the boolean the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key
        
        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getBoolean(key)
        else:
            return table.getBoolean(key, defaultValue)

    @staticmethod
    def putNumber(self, key, value):
        """Put a number in the table.
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :returns: False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putNumber(key, value)

    @staticmethod
    def setDefaultNumber(self, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultNumber(key, defaultValue)

    @staticmethod
    def getNumber(key, defaultValue=_defaultValueSentry):
        """Returns the number the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getNumber(key)
        else:
            return table.getNumber(key, defaultValue)

    @staticmethod
    def putString(self, key, value):
        """Put a string in the table.
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :returns: False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putString(key, value)

    @staticmethod
    def setDefaultString(self, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultString(key, defaultValue)


    @staticmethod
    def getString(key, defaultValue=_defaultValueSentry):
        """Returns the string the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getString(key)
        else:
            return table.getString(key, defaultValue)

    @staticmethod
    def putBooleanArray(self, key, value):
        """Put a boolean array in the table.
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :returns: False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putBooleanArray(key, value)

    @staticmethod
    def setDefaultBooleanArray(self, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultBooleanArray(key, defaultValue)


    @staticmethod
    def getBooleanArray(key, defaultValue=_defaultValueSentry):
        """Returns the boolean array the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getBooleanArray(key)
        else:
            return table.getBooleanArray(key, defaultValue)

    @staticmethod
    def putNumberArray(self, key, value):
        """Put a number array in the table.
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :returns: False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putNumberArray(key, value)

    @staticmethod
    def setDefaultNumberArray(self, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultNumberArray(key, defaultValue)


    @staticmethod
    def getNumberArray(key, defaultValue=_defaultValueSentry):
        """Returns the number array the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getNumberArray(key)
        else:
            return table.getNumberArray(key, defaultValue)

    @staticmethod
    def putRaw(self, key, value):
        """Put a raw value (byte array) in the table.
        :param key: the key to be assigned to
        :param value: the value that will be assigned
        :returns: False if the table key already exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.putRaw(key, value)

    @staticmethod
    def setDefaultRaw(self, key, defaultValue):
        """Gets the current value in the table, setting it if it does not exist.
        :param key: the key
        :param defaultValue: the default value to set if key doens't exist.
        :returns: False if the table key exists with a different type
        """
        table = SmartDashboard.getTable()
        return table.setDefaultNumberArray(key, defaultValue)


    @staticmethod
    def getRaw(key, defaultValue=_defaultValueSentry):
        """Returns the raw value (byte array) the key maps to. If the key does not exist or is of
   *    different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
   *     if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getNumberArray(key)
        else:
            return table.getNumberArray(key, defaultValue)



    # Deprecated Methods
    putInt = putNumber
    getInt = getNumber
    putDouble = putNumber
    getDouble = getNumber
