#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2012. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import threading

import logging
logger = logging.getLogger(__name__)

__all__ = ["Preferences"]

class Preferences:
    """Provides a relatively simple way to save important
    values to the RoboRIO to access the next time the RoboRIO is booted.

    This class loads and saves from a file inside the RoboRIO. The user can not
    access the file directly, but may modify values at specific fields which
    will then be saved to the file when :func:`save` is called.

    This class is thread safe.

    This will also interact with :class:`networktables.NetworkTable` by creating a table
    called "Preferences" with all the key-value pairs. To save using
    `NetworkTable`, simply set the boolean at position ~S A V E~ to true.
    Also, if the value of any variable is " in the `NetworkTable`, then
    that represents non-existence in the `Preferences` table.
    """

    # The Preferences table name
    TABLE_NAME = "Preferences"
    # The value of the save field
    SAVE_FIELD = "~S A V E~"
    # The file to save to
    FILE_NAME = "/home/lvuser/wpilib-preferences.ini"
    # The characters to put between a field and value
    VALUE_PREFIX = '="'
    # The characters to put after the value
    VALUE_SUFFIX = '"\n'
    # The newline character
    NEW_LINE = '\n'

    @staticmethod
    def getInstance():
        """Returns the preferences instance.

        :returns: the preferences instance
        """
        if not hasattr(Preferences, "instance"):
            Preferences.instance = Preferences()
        return Preferences.instance

    def __init__(self):
        """Creates a preference class that will automatically read the file in
        a different thread. Any call to its methods will be blocked until the
        thread is finished reading.
        """
        # The actual values (str->str)
        self.values = {}
        # The keys in the order they were read from the file
        self.keylist = []
        # The comments that were in the file sorted by which key they appeared
        # over (str->str)
        self.comments = {}
        # The comment at the end of the file
        self.endComment = ""

        # The semaphore for beginning reads and writes to the file
        self.fileLock = threading.Condition()
        # The semaphore for reading from the table
        self.lock = threading.RLock()

        # We synchronized on fileLock and then wait
        # for it to know that the reading thread has started
        with self.fileLock:
            reader = threading.Thread(target=self._read,
                                      name="Preferences Read")
            reader.start()
            self.fileLock.wait()

        hal.HALReport(hal.HALUsageReporting.kResourceType_Preferences, 0)

    def getKeys(self):
        """:returns: a list of the keys
        """
        with self.lock:
            return [x for x in self.keylist]

    def keys(self):
        """Python style get list of keys.
        """
        with self.lock:
            return [x for x in self.keylist]

    def put(self, key, value):
        """Puts the given value into the given key position

        :param key: the key
        :param value: the value
        """
        if any((c in key) for c in "=\n\r\t[] "):
            raise KeyError("improper preference key '%s'" % key)
        with self.lock:
            if key not in self.values:
                self.keylist.append(key)
            self.values[key] = value
            try:
                from networktables import NetworkTable
                NetworkTable.getTable(self.TABLE_NAME).putString(key, value)
            except ImportError:
                pass

    def putString(self, key, value):
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
            raise ValueError("Can not put string: '%s' because it contains quotation marks" % value)
        self.put(key, value)

    def putInt(self, key, value):
        """Puts the given int into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.put(key, str(value))

    def putFloat(self, key, value):
        """Puts the given float into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.put(key, str(value))

    def putBoolean(self, key, value):
        """Puts the given float into the preferences table.

        The key may not have any whitespace nor an equals sign.

        This will NOT save the value to memory between power cycles, to
        do that you must call :func:`save` (which must be used with care)
        at some point after calling this.

        :param key: the key
        :param value: the value
        """
        self.put(key, str(value))

    def __setitem__(self, key, value):
        """Python style setting of key/value."""
        if isinstance(value, str):
            self.putString(key, value)
        else:
            self.put(key, str(value))

    def get(self, key, d=None):
        """Returns the value at the given key.

        :param key: the key
        :param d: the return value if the key doesn't exist (default is None)
        :returns: the value (or d/None if none exists)
        """
        with self.lock:
            return self.values.get(key, d)

    def containsKey(self, key):
        """Returns whether or not there is a key with the given name.

        :param key: the key
        :returns: True if there is a value at the given key
        """
        with self.lock:
            return key in self.values

    def __contains__(self, key):
        """Python style contains key."""
        with self.lock:
            return key in self.values

    def has_key(self, key):
        """Python style contains key."""
        with self.lock:
            return key in self.values

    def remove(self, key):
        """Remove a preference

        :param key: the key
        """
        with self.lock:
            self.values.pop(key, None)
            try:
                self.keylist.remove(key)
            except ValueError:
                pass

    def __delitem__(self, key):
        """Python style preference removal
        """
        with self.lock:
            del self.values[key]
            try:
                self.keylist.remove(key)
            except ValueError:
                raise KeyError(key)

    def getString(self, key, backup):
        """Returns the string at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        """
        return self.get(key, backup)

    def getInt(self, key, backup):
        """Returns the int at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        :raises: ValueError if value cannot be converted to integer
        """
        value = self.get(key)
        if value is None:
            return backup
        return int(value)

    def getFloat(self, key, backup):
        """Returns the float at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        :raises: ValueError if value cannot be converted to integer
        """
        value = self.get(key)
        if value is None:
            return backup
        return float(value)

    def getBoolean(self, key, backup):
        """Returns the boolean at the given key. If this table does not have a
        value for that position, then the given backup value will be returned.

        :param key: the key
        :param backup: the value to return if none exists in the table
        :returns: either the value in the table, or the backup
        :raises: ValueError if value cannot be converted to integer
        """
        value = self.get(key)
        if value is None:
            return backup
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise ValueError("invalid literal for boolean: '%s'" % value)

    def save(self):
        """Saves the preferences to a file on the RoboRIO.

        This should NOT be called often. Too many writes can damage the
        RoboRIO's flash memory. While it is ok to save once or twice a match,
        this should never be called every run of
        :func:`IterativeRobot.teleopPeriodic`.

        The actual writing of the file is done in a separate thread. However,
        any call to a get or put method will wait until the table is fully
        saved before continuing.
        """
        with self.fileLock:
            writer = threading.Thread(target=self._write,
                                      name="Preferences Write")
            writer.start()
            self.fileLock.wait()

    def _write(self):
        """Internal method that actually writes the table to a file. This is
        called in its own thread when :func:`save` is called.
        """
        with self.lock:
            with self.fileLock:
                self.fileLock.notify_all()

            with open(self.FILE_NAME, "w") as output:
                output.write("[Preferences]\n")
                for key in self.keylist:
                    value = self.values.get(key, "")
                    comment = self.comments.get(key, "")
                    if comment:
                        output.write(comment)

                    output.write(key)
                    output.write(self.VALUE_PREFIX)
                    output.write(value)
                    output.write(self.VALUE_SUFFIX)

                output.write(self.endComment)

            try:
                from networktables import NetworkTable
                NetworkTable.getTable(self.TABLE_NAME).putBoolean(self.SAVE_FIELD, False)
            except ImportError:
                pass

    def read(self):
        """The internal method to read from a file. This will be called in its
        own thread when the preferences singleton is first created.
        """

        with self.lock:
            with self.fileLock:
                self.fileLock.notify_all()

            comment = []

            try:
                with open(self.FILE_NAME) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            comment.append(self.NEW_LINE)
                        elif line[0] == ';':
                            comment.append(line)
                            comment.append(self.NEW_LINE)
                        elif line[0] == '[':
                            continue # throw it away
                        else:
                            name, value = line.partition('=')
                            name = name.strip()
                            value = value.strip()

                            # Get between quotes if it starts with a quote
                            if value and value[0] == '"':
                                value = value[1:].partition('"')[0]

                            self.keylist.append(name)
                            self.values[name] = value
                            try:
                                from networktables import NetworkTable
                                NetworkTable.getTable(self.TABLE_NAME).putString(name, value)
                            except ImportError:
                                pass

                            if comment:
                                self.comments[name] = "".join(comment)
                                comment = []
            except FileNotFoundError:
                pass

            if comment:
                self.endComment = "".join(comment)

            logger.info("Done reading preferences")

        try:
            from networktables import NetworkTable
            NetworkTable.getTable(self.TABLE_NAME).putBoolean(self.SAVE_FIELD, False)
            # TODO: Verify that this works even though it changes with
            # subtables. Should work since preferences shouldn't have subtables.
            NetworkTable.getTable(self.TABLE_NAME).addTableListener(self.valueChanged)
        except ImportError:
            pass

    def valueChanged(self, source, key, value, isNew):
        if key == self.SAVE_FIELD:
            if value:
                self.save()
        else:
            with self.lock:
                if any((c in key) for c in "=\n\r\t[] ") or '"' in str(value):
                    if key in self.values or key in self.keylist:
                        self.values.pop(key, None)
                        try:
                            self.keylist.remove(key)
                        except ValueError:
                            pass
                        try:
                            from networktables import NetworkTable
                            NetworkTable.getTable(self.TABLE_NAME).putString(key, '"')
                        except ImportError:
                            pass
                else:
                    if key not in self.values:
                        self.keylist.append(key)
                    self.values[key] = str(value)
