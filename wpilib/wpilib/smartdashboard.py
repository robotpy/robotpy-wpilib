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
    def putBoolean(key, value):
        """Maps the specified key to the specified value in this table.
        The key can not be None.
        
        The value can be retrieved by calling the get method with a key that
        is equal to the original key.
        
        :param key: the key
        :type  key: str
        :param value: the value
        """
        table = SmartDashboard.getTable()
        table.putBoolean(key, value)

    @staticmethod
    def getBoolean(key, defaultValue=_defaultValueSentry):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :returns: the value
        
        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getBoolean(key)
        else:
            return table.getBoolean(key, defaultValue)

    @staticmethod
    def putNumber(key, value):
        """Maps the specified key to the specified value in this table.
        The key can not be None.
        The value can be retrieved by calling the get method with a key that
        is equal to the original key.
        
        :param key: the key
        :type  key: str
        :param value: the value
        :type  value: int or float
        """
        table = SmartDashboard.getTable()
        table.putNumber(key, value)

    @staticmethod
    def getNumber(key, defaultValue=_defaultValueSentry):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :rtype: float
        
        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getNumber(key)
        else:
            return table.getNumber(key, defaultValue)

    @staticmethod
    def putString(key, value):
        """Maps the specified key to the specified value in this table.
        The key can not be None.
        The value can be retrieved by calling the get method with a key that
        is equal to the original key.
        
        :param key: the key
        :type  key: str
        :param value: the value
        :type  value: str
        """
        table = SmartDashboard.getTable()
        table.putString(key, value)

    @staticmethod
    def getString(key, defaultValue=_defaultValueSentry):
        """Returns the value at the specified key.
        
        :param key: the key
        :type  key: str
        :param defaultValue: returned if the key doesn't exist
        :rtype: str
        
        :raises: :exc:`KeyError` if the key doesn't exist and defaultValue
                 is not provided.
        """
        table = SmartDashboard.getTable()
        if defaultValue is SmartDashboard._defaultValueSentry:
            return table.getString(key)
        else:
            return table.getString(key, defaultValue)

    # Deprecated Methods
    putInt = putNumber
    getInt = getNumber
    putDouble = putNumber
    getDouble = getNumber
