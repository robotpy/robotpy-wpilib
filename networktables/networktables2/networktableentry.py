class NetworkTableEntry:
    """An entry in a network table
    """
    # the id that represents that an id is unknown for an entry
    UNKNOWN_ID = 0xFFFF
    HALF_OF_CHAR = 32768

    def __init__(self, name, type, value, id=UNKNOWN_ID, sequenceNumber=0):
        """Create a new entry with the given id, name, sequence number, type
        and value
        :param name: the name of the entry
        :param type: the type of the entry
        :param value:
        :param id:
        :param sequenceNumber:
        """
        self.id = id
        self.name = name
        self.sequenceNumber = sequenceNumber
        self.type = type
        self.value = value
        self.isNew = True
        self.isDirty = False

    def getId(self):
        """:returns: the id of the entry
        """
        return self.id

    def getValue(self):
        """:returns: the current value of the entry
        """
        return self.value

    def getType(self):
        """:returns: the type of the entry
        """
        return self.type

    def putValue(self, newSequenceNumber, newValue):
        """set the value of the entry if the given sequence number is greater
        that the current sequence number
        :param newSequenceNumber: the sequence number of the incoming entry
        :param newValue: the new value
        :returns: True if the value was set
        """
        if ((self.sequenceNumber < newSequenceNumber and
             (newSequenceNumber - self.sequenceNumber) < self.HALF_OF_CHAR) or
            (self.sequenceNumber > newSequenceNumber and
             (self.sequenceNumber - newSequenceNumber) > self.HALF_OF_CHAR)):
            self.value = newValue
            self.sequenceNumber = newSequenceNumber
            return True
        return False

    def forcePut(self, newSequenceNumber, newValue, type=None):
        """force a value and new sequence number upon an entry.
        If specified, will also set the type of the entry.
        :param newSequenceNumber:
        :param type:
        :param newValue:
        """
        if type is not None:
            self.type = type
        self.value = newValue
        self.sequenceNumber = newSequenceNumber

    def makeDirty(self):
        self.isDirty = True

    def makeClean(self):
        self.isDirty = False

    def sendValue(self, wstream):
        """Send the value of the entry over the output stream
        :param wstream: output stream
        """
        self.type.sendValue(self.value, wstream)

    def getSequenceNumber(self):
        """:returns: the current sequence number of the entry
        """
        return self.sequenceNumber

    def setId(self, id):
        """Sets the id of the entry
        :param id: the id of the entry
        Raises ValueError if the entry already has a known id
        """
        if self.id != self.UNKNOWN_ID:
            raise ValueError("Cannot set the Id of a table entry that already has a valid id")
        self.id = id

    def clearId(self):
        """clear the id of the entry to unknown
        """
        self.id = self.UNKNOWN_ID

    def send(self, connection):
        connection.sendEntryAssignment(self)

    def fireListener(self, listenerManager):
        #TODO determine best way to handle complex data
        listenerManager.fireTableListeners(self.name, self.value, self.isNew)
        self.isNew = False

    def __str__(self):
        return "Network Table %s entry: %s: %d - %d - %s" % \
                (self.type.name, self.name, self.id, self.sequenceNumber,
                 self.value)
