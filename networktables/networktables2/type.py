class ComplexData:
    def __init__(self, type):
        self.type = type

    def getType(self):
        return self.type

class ArrayData(ComplexData, list):
    def __init__(self, type):
        ComplexData.__init__(self, type)
        list.__init__(self)

class NetworkTableEntryType:
    """A class defining the types supported by NetworkTables as well as
    support for serialization of those types to and from DataStreams
    """

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return "NetworkTable type: %s" % self.name

    def sendValue(self, value, wstream):
        """send a value over a data output stream
        :param value: the value to send
        :param wstream: the stream to send the value over
        """
        raise NotImplementedError

    def readValue(self, rstream):
        """read a value from a data input stream
        :param rstream: the stream to read a value from
        :returns: the value read from the stream
        """
        raise NotImplementedError

class DefaultEntryTypes:
    BOOLEAN_RAW_ID = 0x00
    DOUBLE_RAW_ID = 0x01
    STRING_RAW_ID = 0x02

    class Boolean(NetworkTableEntryType):
        """a boolean entry type
        """
        def __init__(self):
            super().__init__(DefaultEntryTypes.BOOLEAN_RAW_ID, "Boolean")
        def sendValue(self, value, wstream):
            wstream.writeBoolean(bool(value))
        def readValue(self, rstream):
            return rstream.readBoolean()

    class Double(NetworkTableEntryType):
        """a double floating point type
        """
        def __init__(self):
            super().__init__(DefaultEntryTypes.DOUBLE_RAW_ID, "Double")
        def sendValue(self, value, wstream):
            wstream.writeDouble(float(value))
        def readValue(self, rstream):
            return rstream.readDouble()

    class String(NetworkTableEntryType):
        """a string type
        """
        def __init__(self):
            super().__init__(DefaultEntryTypes.STRING_RAW_ID, "String")
        def sendValue(self, value, wstream):
            wstream.writeUTF(str(value))
        def readValue(self, rstream):
            return rstream.readUTF()

DefaultEntryTypes.BOOLEAN = DefaultEntryTypes.Boolean()
DefaultEntryTypes.DOUBLE = DefaultEntryTypes.Double()
DefaultEntryTypes.STRING = DefaultEntryTypes.String()

class ComplexEntryType(NetworkTableEntryType):
    def __init__(self, id, name):
        super().__init__(id, name)

    def internalizeValue(self, key, externalRepresentation, currentInteralValue):
        raise NotImplementedError

    def exportValue(self, key, internalData, externalRepresentation):
        raise NotImplementedError

class ArrayEntryType(ComplexEntryType):
    #TODO allow for array of complex type
    def __init__(self, id, elementType, externalArrayType):
        super().__init__(id, "Array of [%s]" % elementType.name)
        if not issubclass(externalArrayType, ArrayData):
            raise TypeError("External Array Data Type must extend ArrayData")
        self.externalArrayType = externalArrayType
        self.elementType = elementType

    def sendValue(self, value, wstream):
        if len(value) > 255:
            raise IOError("Cannot write %s as %s. Arrays have a max length of 255 values" % (value, self.name))
        wstream.writeByte(len(value))
        for v in value:
            self.elementType.sendValue(v, wstream)

    def readValue(self, rstream):
        length = rstream.readUnsignedByte()
        dataArray = [] #TODO cache object arrays
        for i in range(length):
            dataArray.append(self.elementType.readValue(rstream))
        return dataArray

    def internalizeValue(self, key, externalRepresentation, currentInternalValue):
        if not isinstance(externalRepresentation, self.externalArrayType):
            raise TypeError("%s is not a %s" % (externalRepresentation, self.externalArrayType))

        if len(currentInternalValue) == len(externalRepresentation):
            internalArray = currentInternalValue
            internalArray.clear()
        else:
            internalArray = []
        internalArray.extend(externalRepresentation)
        return internalArray

    def exportValue(self, key, internalData, externalRepresentation):
        if not isinstance(externalRepresentation, self.externalArrayType):
            raise TypeError("%s is not a %s" % (externalRepresentation, self.externalArrayType))

        externalRepresentation.clear()
        externalRepresentation.extend(internalData)

class BooleanArray(ArrayData):
    BOOLEAN_ARRAY_RAW_ID = 0x10

    def __init__(self):
        super().__init__(BooleanArray.TYPE)

    def __contains__(self, key):
        return super().__contains__(bool(key))

    def __setitem__(self, key, value):
        super().__setitem(key, bool(value))

    def append(self, obj):
        super().append(bool(obj))

    def extend(self, iterable):
        super().extend(bool(x) for x in iterable)

    def insert(self, index, obj):
        super().insert(index, bool(obj))

    def remove(self, value):
        super().remove(bool(value))

BooleanArray.TYPE = ArrayEntryType(BooleanArray.BOOLEAN_ARRAY_RAW_ID,
                                   DefaultEntryTypes.BOOLEAN,
                                   BooleanArray)

class NumberArray(ArrayData):
    NUMBER_ARRAY_RAW_ID = 0x11

    def __init__(self):
        super().__init__(NumberArray.TYPE)

    def __contains__(self, key):
        return super().__contains__(float(key))

    def __setitem__(self, key, value):
        super().__setitem(key, float(value))

    def append(self, obj):
        super().append(float(obj))

    def extend(self, iterable):
        super().extend(float(x) for x in iterable)

    def insert(self, index, obj):
        super().insert(index, float(obj))

    def remove(self, value):
        super().remove(float(value))

NumberArray.TYPE = ArrayEntryType(NumberArray.NUMBER_ARRAY_RAW_ID,
                                  DefaultEntryTypes.DOUBLE,
                                  NumberArray)

class StringArray(ArrayData):
    STRING_ARRAY_RAW_ID = 0x12

    def __init__(self):
        super().__init__(StringArray.TYPE)

    def __contains__(self, key):
        return super().__contains__(str(key))

    def __setitem__(self, key, value):
        super().__setitem(key, str(value))

    def append(self, obj):
        super().append(str(obj))

    def extend(self, iterable):
        super().extend(str(x) for x in iterable)

    def insert(self, index, obj):
        super().insert(index, str(obj))

    def remove(self, value):
        super().remove(str(value))

StringArray.TYPE = ArrayEntryType(StringArray.STRING_ARRAY_RAW_ID,
                                  DefaultEntryTypes.STRING,
                                  StringArray)

class NetworkTableEntryTypeManager:
    def __init__(self):
        self.typeMap = {}
        self.registerType(DefaultEntryTypes.BOOLEAN)
        self.registerType(DefaultEntryTypes.DOUBLE)
        self.registerType(DefaultEntryTypes.STRING)
        self.registerType(BooleanArray.TYPE)
        self.registerType(NumberArray.TYPE)
        self.registerType(StringArray.TYPE)

    def getType(self, id):
        return self.typeMap.get(id)

    def registerType(self, type):
        self.typeMap[type.id] = type
