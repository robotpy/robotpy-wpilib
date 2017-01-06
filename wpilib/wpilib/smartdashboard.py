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
    
    @classmethod
    def _reset(cls):
        cls.tablesToData = {}
        cls.table = None

    @classmethod
    def getTable(cls):
        if cls.table is None:
            from networktables import NetworkTable
            cls.table = NetworkTable.getTable("SmartDashboard")
            hal.report(hal.UsageReporting.kResourceType_SmartDashboard,
                       hal.UsageReporting.kSmartDashboard_Instance)
        return cls.table

    @classmethod
    def putData(cls, *args, **kwargs):
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

        table = cls.getTable()
        dataTable = table.getSubTable(key)
        dataTable.putString("~TYPE~", data.getSmartDashboardType())
        data.initTable(dataTable)
        cls.tablesToData[dataTable] = data

    @classmethod
    def getData(cls, key):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        :returns: the value
        
        :raises: :exc:`KeyError` if the key doesn't exist
        """
        table = cls.getTable()
        subtable = table.getSubTable(key)
        data = cls.tablesToData.get(subtable)
        if data is None:
            raise KeyError("SmartDashboard data does not exist: '%s'" % key)
        return data

    @classmethod
    def containsKey(cls, key):
        """Checks the table and tells if it contains the specified key.

        :param key: key the key to search for
        :return: true if the table as a value assigned to the given key
        """
        table = cls.getTable()
        return table.containsKey(key)

    @classmethod
    def getKeys(cls, types=0):
        """Get array of keys in the table.

        :param types: bitmask of types; 0 is treated as a "don't care".
        :return: keys currently in the table
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
        :return: True if the value is persistent.
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
        table.clearFlags()

    @classmethod
    def getFlags(cls, key):
        """ Returns the flags for the specified key.

        :param key: the key name
        :return: the flags, or 0 if the key is not defined
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
    def getBoolean(cls, key, defaultValue=_defaultValueSentry):
        """Returns the boolean the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key
        
        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getBoolean(key)
        else:
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
    def getNumber(cls, key, defaultValue=_defaultValueSentry):
        """Returns the number the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getNumber(key)
        else:
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
    def getString(cls, key, defaultValue=_defaultValueSentry):
        """Returns the string the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getString(key)
        else:
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
    def getBooleanArray(cls, key, defaultValue=_defaultValueSentry):
        """Returns the boolean array the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getBooleanArray(key)
        else:
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
    def getNumberArray(cls, key, defaultValue=_defaultValueSentry):
        """Returns the number array the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getNumberArray(key)
        else:
            return table.getNumberArray(key, defaultValue)

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
        return table.setDefaultNumberArray(key, defaultValue)


    @classmethod
    def getRaw(cls, key, defaultValue=_defaultValueSentry):
        """Returns the raw value (byte array) the key maps to. If the key does not exist or is of
        different type, it will return the default value; if that is not provided,
        it will throw a :exc:`KeyError`.
        
        Calling this method without passing defaultValue is deprecated.

        :param key: the key to look up
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value associated with the given key or the given default value
                  if there is no value associated with the key

        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = cls.getTable()
        if defaultValue is cls._defaultValueSentry:
            return table.getNumberArray(key)
        else:
            return table.getNumberArray(key, defaultValue)



    # Deprecated Methods
    putInt = putNumber
    getInt = getNumber
    putDouble = putNumber
    getDouble = getNumber
