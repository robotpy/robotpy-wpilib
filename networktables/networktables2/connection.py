import struct
import threading

from .networktableentry import NetworkTableEntry

__all__ = ["BadMessageError", "StreamEOF", "NetworkTableConnection",
           "ConnectionMonitorThread", "PROTOCOL_REVISION"]

class BadMessageError(IOError):
    pass

class StreamEOF(IOError):
    pass

PROTOCOL_REVISION = 0x0200

# The definitions of all of the protocol message types

class Message:
    def __init__(self, HEADER, STRUCT=None):
        self.HEADER = HEADER
        if STRUCT is None:
            self.STRUCT = None
        else:
            self.STRUCT = struct.Struct(STRUCT)

    def send(self, wstream, *args):
        wstream.write(self.HEADER)
        if self.STRUCT is not None:
            wstream.write(self.STRUCT.pack(*args))

    def read(self, rstream):
        return rstream.readStruct(self.STRUCT)

class NamedMessage(Message):
    NAME_LEN_STRUCT = struct.Struct('>H')

    def __init__(self, HEADER, STRUCT=None):
        super().__init__(HEADER, STRUCT)

    def send(self, wstream, name, *args):
        wstream.write(self.HEADER)
        name = name.encode('utf-8')
        wstream.write(self.NAME_LEN_STRUCT.pack(len(name)))
        wstream.write(name)
        if self.STRUCT is not None:
            wstream.write(self.STRUCT.pack(*args))

    def read(self, rstream):
        nameLen = rstream.readStruct(self.NAME_LEN_STRUCT)[0]
        name = rstream.read(nameLen).decode('utf-8')
        return name, rstream.readStruct(self.STRUCT)

# A keep alive message that the client sends
KEEP_ALIVE = Message(b'\x00')
# A client hello message that a client sends
CLIENT_HELLO = Message(b'\x01', '>H')
# A protocol version unsupported message that the server sends to a client
PROTOCOL_UNSUPPORTED = Message(b'\x02', '>H')
# A server hello complete message that a server sends
SERVER_HELLO_COMPLETE = Message(b'\x03')
# An entry assignment message
ENTRY_ASSIGNMENT = NamedMessage(b'\x10', '>bHH')
# A field update message
FIELD_UPDATE = Message(b'\x11', '>HH')

class ReadStream:
    def __init__(self, f):
        self.f = f

    def read(self, size=-1):
        data = self.f.read(size)
        if size is not None and size > 0 and len(data) != size:
            raise StreamEOF("end of file")
        return data

    def readStruct(self, s):
        data = self.f.read(s.size)
        if len(data) != s.size:
            raise StreamEOF("end of file")
        return s.unpack(data)

class NetworkTableConnection:
    """An abstraction for the NetworkTable protocol
    """
    def __init__(self, stream, typeManager):
        self.stream = stream
        self.rstream = ReadStream(stream.getInputStream())
        self.wstream = stream.getOutputStream()
        self.typeManager = typeManager
        self.write_lock = threading.RLock()
        self.isValid = True

    def close(self):
        if self.isValid:
            self.isValid = False
            self.stream.close()

    def flush(self):
        with self.write_lock:
            self.wstream.flush()

    def sendKeepAlive(self):
        with self.write_lock:
            KEEP_ALIVE.send(self.wstream)
            self.flush()

    def sendClientHello(self):
        with self.write_lock:
            CLIENT_HELLO.send(self.wstream, PROTOCOL_REVISION)
            self.flush()

    def sendServerHelloComplete(self):
        with self.write_lock:
            SERVER_HELLO_COMPLETE.send(self.wstream)
            self.flush()

    def sendProtocolVersionUnsupported(self):
        with self.write_lock:
            PROTOCOL_UNSUPPORTED.send(self.wstream, PROTOCOL_REVISION)
            self.flush()

    def sendEntryAssignment(self, entry):
        with self.write_lock:
            ENTRY_ASSIGNMENT.send(self.wstream, entry.name, entry.getType().id,
                                  entry.getId(), entry.getSequenceNumber())
            entry.sendValue(self.wstream)

    def sendEntryUpdate(self, entry):
        with self.write_lock:
            FIELD_UPDATE.send(self.wstream, entry.getId(),
                              entry.getSequenceNumber())
            entry.sendValue(self.wstream)

    def read(self, adapter):
        messageType = self.rstream.read(1)
        if messageType == KEEP_ALIVE.HEADER:
            adapter.keepAlive()
        elif messageType == CLIENT_HELLO.HEADER:
            protocolRevision = CLIENT_HELLO.read(self.rstream)[0]
            adapter.clientHello(protocolRevision)
        elif messageType == SERVER_HELLO_COMPLETE.HEADER:
            adapter.serverHelloComplete()
        elif messageType == PROTOCOL_UNSUPPORTED.HEADER:
            protocolRevision = PROTOCOL_UNSUPPORTED.read(self.rstream)[0]
            adapter.protocolVersionUnsupported(protocolRevision)
        elif messageType == ENTRY_ASSIGNMENT.HEADER:
            entryName, (typeId, entryId, entrySequenceNumber) = \
                    ENTRY_ASSIGNMENT.read(self.rstream)
            entryType = self.typeManager.getType(typeId)
            if entryType is None:
                raise BadMessageError("Unknown data type: 0x%x" % typeId)
            value = entryType.readValue(self.rstream)
            adapter.offerIncomingAssignment(NetworkTableEntry(entryName, entryType, value, id=entryId, sequenceNumber=entrySequenceNumber))
        elif messageType == FIELD_UPDATE.HEADER:
            entryId, entrySequenceNumber = FIELD_UPDATE.read(self.rstream)
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
