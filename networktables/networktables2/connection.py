import threading

from .networktableentry import NetworkTableEntry
from .stream import ReadStream, WriteStream

__all__ = ["BadMessageError", "NetworkTableConnection",
           "ConnectionMonitorThread"]

class BadMessageError(IOError):
    pass

class NetworkTableMessageType:
    """The definitions of all of the protocol message types

    - KEEP_ALIVE: A keep alive message that the client sends
    - CLIENT_HELLO: a client hello message that a client sends
    - PROTOCOL_VERSION_UNSUPPORTED: a protocol version unsupported message
        that the server sends to a client
    - ENTRY_ASSIGNMENT: an entry assignment message
    - FIELD_UPDATE: a field update message
    """
    KEEP_ALIVE = 0x00
    CLIENT_HELLO = 0x01
    PROTOCOL_VERSION_UNSUPPORTED = 0x02
    SERVER_HELLO_COMPLETE = 0x03
    ENTRY_ASSIGNMENT = 0x10
    FIELD_UPDATE = 0x11

class NetworkTableConnection:
    """An abstraction for the NetworkTable protocol
    """
    PROTOCOL_REVISION = 0x0200

    def __init__(self, stream, typeManager):
        self.stream = stream
        self.rstream = ReadStream(stream.getInputStream())
        self.wstream = WriteStream(stream.getOutputStream())
        self.typeManager = typeManager
        self.write_lock = threading.RLock()
        self.isValid = True

    def close(self):
        if self.isValid:
            self.isValid = False
            self.stream.close()

    def sendMessageHeader(self, messageType):
        with self.write_lock:
            self.wstream.writeByte(messageType)

    def flush(self):
        with self.write_lock:
            self.wstream.flush()

    def sendKeepAlive(self):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.KEEP_ALIVE)
            self.flush()

    def sendClientHello(self):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.CLIENT_HELLO)
            self.wstream.writeChar(self.PROTOCOL_REVISION)
            self.flush()

    def sendServerHelloComplete(self):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.SERVER_HELLO_COMPLETE)
            self.flush()

    def sendProtocolVersionUnsupported(self):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.PROTOCOL_VERSION_UNSUPPORTED)
            self.wstream.writeChar(self.PROTOCOL_REVISION)
            self.flush()

    def sendEntryAssignment(self, entry):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.ENTRY_ASSIGNMENT)
            self.wstream.writeUTF(entry.name)
            self.wstream.writeByte(entry.getType().id)
            self.wstream.writeChar(entry.getId())
            self.wstream.writeChar(entry.getSequenceNumber())
            entry.sendValue(self.wstream)

    def sendEntryUpdate(self, entry):
        with self.write_lock:
            self.sendMessageHeader(NetworkTableMessageType.FIELD_UPDATE)
            self.wstream.writeChar(entry.getId())
            self.wstream.writeChar(entry.getSequenceNumber())
            entry.sendValue(self.wstream)

    def read(self, adapter):
        messageType = self.rstream.readByte()
        if messageType == NetworkTableMessageType.KEEP_ALIVE:
            adapter.keepAlive()
        elif messageType == NetworkTableMessageType.CLIENT_HELLO:
            protocolRevision = self.rstream.readChar()
            adapter.clientHello(protocolRevision)
        elif messageType == NetworkTableMessageType.SERVER_HELLO_COMPLETE:
            adapter.serverHelloComplete()
        elif messageType == NetworkTableMessageType.PROTOCOL_VERSION_UNSUPPORTED:
            protocolRevision = self.rstream.readChar()
            adapter.protocolVersionUnsupported(protocolRevision)
        elif messageType == NetworkTableMessageType.ENTRY_ASSIGNMENT:
            entryName = self.rstream.readUTF()
            typeId = self.rstream.readByte()
            entryType = self.typeManager.getType(typeId)
            if entryType is None:
                raise BadMessageError("Unknown data type: 0x%x" % typeId)
            entryId = self.rstream.readChar()
            entrySequenceNumber = self.rstream.readChar()
            value = entryType.readValue(self.rstream)
            adapter.offerIncomingAssignment(NetworkTableEntry(entryName, entryType, value, id=entryId, sequenceNumber=entrySequenceNumber))
        elif messageType == NetworkTableMessageType.FIELD_UPDATE:
            entryId = self.rstream.readChar()
            entrySequenceNumber = self.rstream.readChar()
            entry = adapter.getEntry(entryId)
            if entry is None:
                raise BadMessageError("Received update for unknown entry id: %d " % entryId)
            value = entry.getType().readValue(self.rstream)
            adapter.offerIncomingUpdate(entry, entrySequenceNumber, value)
        else:
            raise BadMessageError("Unknown Network Table Message Type: %s" % (messageType))

class ConnectionMonitorThread(threading.Thread):
    """A periodic thread that repeatedly reads from a connection
    """
    def __init__(self, adapter, connection, name=None):
        """create a new monitor thread
        :param adapter:
        :param connection:
        """
        super().__init__(name=name)
        self.adapter = adapter
        self.connection = connection
        self.running = True

    def stop(self):
        self.running = False
        try:
            self.join()
        except RuntimeError:
            pass

    def run(self):
        while self.running:
            try:
                self.connection.read(self.adapter)
            except BadMessageError as e:
                self.adapter.badMessage(e)
            except IOError as e:
                self.adapter.ioError(e)
