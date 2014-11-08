from .type import DefaultEntryTypes, ComplexData, ComplexEntryType

__all__ = ["NetworkTableNode"]

class NetworkTableNode:
    """represents a node (either a client or a server) in a network tables 2.0
    """

    def __init__(self, entryStore):
        self.entryStore = entryStore
        self.remoteListeners = []
        self.tableListeners = []

    def getEntryStore(self):
        """:returns: the entry store used by this node
        """
        return self.entryStore

    def putBoolean(self, name, value):
        self.putValue(name, value, type=DefaultEntryTypes.BOOLEAN)

    def getBoolean(self, name):
        entry = self.entryStore.getEntry(name)
        if entry is None:
            raise KeyError(name)
        return bool(entry.getValue())

    def putDouble(self, name, value):
        self.putValue(name, value, type=DefaultEntryTypes.DOUBLE)

    def getDouble(self, name):
        entry = self.entryStore.getEntry(name)
        if entry is None:
            raise KeyError(name)
        return float(entry.getValue())

    def putString(self, name, value):
        self.putValue(name, value, type=DefaultEntryTypes.STRING)

    def getString(self, name):
        entry = self.entryStore.getEntry(name)
        if entry is None:
            raise KeyError(name)
        return str(entry.getValue())

    def putComplex(self, name, value):
        self.putValue(name, value, type=value.getType())

    def retrieveValue(self, name, externalData):
        with self.entryStore.mutex:
            entry = self.entryStore.getEntry(name)
            if entry is None:
                raise KeyError(name)
            entryType = entry.getType()
            if not isinstance(entryType, ComplexEntryType):
                raise TypeError("'%s' is not a complex data type" % name)
            entryType.exportValue(name, entry.getValue(), externalData)

    def putValue(self, name, value, type=None):
        """Put a value with a specific network table type
        :param name: the name of the entry to associate with the given value
        :param value: the actual value of the entry
        :param type: the type of the entry (if not provided, will be guessed)
        """
        if type is None:
            # Guess type based on value
            if isinstance(value, float):
                type = DefaultEntryTypes.DOUBLE
            elif isinstance(value, str):
                type = DefaultEntryTypes.STRING
            elif isinstance(value, bool):
                type = DefaultEntryTypes.BOOLEAN
            elif isinstance(value, ComplexData):
                type = value.getType()
            elif value is None:
                raise ValueError("Cannot put a null value into networktables")
            else:
                raise ValueError("Invalid Type")

        if isinstance(type, ComplexEntryType):
            with self.entryStore.mutex: #must sync because use get
                entry = self.entryStore.getEntry(name)
                if entry is not None:
                    self.entryStore.putOutgoingEntry(entry, type.internalizeValue(entry.name, value, entry.getValue()))
                else:
                    self.entryStore.putOutgoing(name, type, type.internalizeValue(name, value, None))
        else:
            self.entryStore.putOutgoing(name, type, value)

    def putValueEntry(self, entry, value):
        """Put a value into a specific entry
        :param entry: the entry to associate with the given value
        :param value: the actual value of the entry
        """
        entryType = entry.getType()
        if isinstance(entryType, ComplexEntryType):
            with self.entryStore.mutex: #must sync because use get
                self.entryStore.putOutgoingEntry(entry, entryType.internalizeValue(entry.name, value, entry.getValue()))
        else:
            self.entryStore.putOutgoingEntry(entry, value)
        return

    def getValue(self, name):
        #TODO don't allow get of complex types
        with self.entryStore.mutex:
            entry = self.entryStore.getEntry(name)
            if entry is None:
                raise KeyError(name)
            return entry.getValue()

    def containsKey(self, key):
        """:param key: the key to check for existence
        :returns: True if the table has the given key
        """
        return self.entryStore.getEntry(key) is not None

    def __contains__(self, key):
        return self.entryStore.getEntry(key) is not None

    def close(self):
        """close all networking activity related to this node
        """
        pass

    def addConnectionListener(self, listener, immediateNotify):
        self.remoteListeners.append(listener)
        if self.isConnected():
            listener.connected(self)
        else:
            listener.disconnected(self)

    def removeConnectionListener(self, listener):
        self.remoteListeners.remove(listener)

    def fireConnectedEvent(self):
        for listener in self.remoteListeners:
            listener.connected(self)

    def fireDisconnectedEvent(self):
        for listener in self.remoteListeners:
            listener.disconnected(self)

    def addTableListener(self, listener, immediateNotify):
        self.tableListeners.append(listener)
        if immediateNotify:
            self.entryStore.notifyEntries(None, listener)

    def removeTableListener(self, listener):
        self.tableListeners.remove(listener)

    def fireTableListeners(self, key, value, isNew):
        for listener in self.tableListeners:
            listener.valueChanged(None, key, value, isNew)
