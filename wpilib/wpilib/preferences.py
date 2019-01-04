# validated: 2019-01-04 DS 3178911eef5 edu/wpi/first/wpilibj/Preferences.java
# ----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import logging
from typing import List, Optional

from networktables import NetworkTables

import hal


logger = logging.getLogger(__name__)

__all__ = ["Preferences"]


class Preferences:
    """Provides a relatively simple way to save important
    values to the roboRIO to access the next time the roboRIO is booted.

    This class loads and saves from a file inside the roboRIO. The user can not
    access the file directly, but may modify values at specific fields which
    will then be saved to the file when :func:`save` is called.

    This class is thread safe.

    This will also interact with :class:`networktables.NetworkTable` by creating a table
    called "Preferences" with all the key-value pairs. To save using
    `NetworkTable`, simply set the boolean at position ~S A V E~ to true.
    Also, if the value of any variable is " in the `NetworkTable`, then
    that represents non-existence in the `Preferences` table.

    .. not_implemented: putDouble, putLong, getDouble, getLong
    """

    # The Preferences table name
    TABLE_NAME = "Preferences"

    @staticmethod
    def getInstance() -> "Preferences":
        """Returns the preferences instance.

        :returns: the preferences instance
        """
        if not hasattr(Preferences, "instance"):
            Preferences.instance = Preferences()
        return Preferences.instance

    @classmethod
    def _reset(cls) -> None:
        if hasattr(cls, "instance"):
            del cls.instance

    def __init__(self) -> None:
        """Creates a preference class that will automatically read the file in
        a different thread. Any call to its methods will be blocked until the
        thread is finished reading.
        """
        self.table = NetworkTables.getTable(self.TABLE_NAME)
        self.table.addTableListenerEx(
            self.valueChangedEx,
            NetworkTables.NotifyFlags.NEW | NetworkTables.NotifyFlags.IMMEDIATE,
        )

        hal.report(hal.UsageReporting.kResourceType_Preferences, 0)

    def getKeys(self) -> List[str]:
        """:returns: a list of the keys
        """
        with self.lock:
            return [x for x in self.table.getKeys()]

    def keys(self) -> List[str]:
        """Python style get list of keys.
        """
        with self.lock:
            return [x for x in self.table.getKeys()]

    def putString(self, key: str, value: str) -> None:
        """Puts the given string into the preferences table.

        The value may not have quotation marks, nor may the key have any
        whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        if '"' in value:
            raise ValueError(
                "Can not put string: '%s' because it contains quotation marks" % value
            )
        self.table.putString(key, value)
        self.table.setPersistent(key)

    def putInt(self, key: str, value: int) -> None:
        """Puts the given int into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.table.putNumber(key, value)
        self.table.setPersistent(key)

    def putFloat(self, key: str, value: float) -> None:
        """Puts the given float into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.table.putNumber(key, value)
        self.table.setPersistent(key)

    def putBoolean(self, key: str, value: bool) -> None:
        """Puts the given float into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.table.putBoolean(key, value)
        self.table.setPersistent(key)

    def __setitem__(self, key, value):
        """Python style setting of key/value."""
        self.table.putString(key, str(value))

    def containsKey(self, key: str) -> bool:
        """Returns whether or not there is a key with the given name.

        :param key: the key
        :returns: True if there is a value at the given key
        """
        return self.table.containsKey(key)

    def __contains__(self, key):
        """Python style contains key."""
        return self.table.containsKey(key)

    def remove(self, key: str) -> None:
        """Remove a preference

        :param key: the key
        """
        self.table.delete(key)

    def __delitem__(self, key):
        """Python style preference removal
        """
        self.table.delete(key)

    def getString(self, key: str, backup: Optional[str] = None) -> str:
        """Returns the string at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        """
        return self.table.getString(key, backup)

    def getInt(self, key: str, backup: Optional[int] = None) -> int:
        """Returns the int at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        :raises: TableKeyNotDefinedException if key cannot be found
        """
        return self.table.getNumber(key, backup)

    def getFloat(self, key: str, backup: Optional[float] = None) -> float:
        """Returns the float at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        :raises: TableKeyNotDefinedException if key cannot be found
        """
        return self.table.getNumber(key, backup)

    def getBoolean(self, key: str, backup: Optional[bool] = None) -> bool:
        """Returns the boolean at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        """
        return self.table.getBoolean(key, backup)

    def valueChangedEx(self, source, key, value, isNew) -> None:
        self.table.setPersistent(key)
