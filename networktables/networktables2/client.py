import threading

from .common import *
from .connection import *
from .networktableentry import NetworkTableEntry
from .networktablenode import NetworkTableNode
from .type import NetworkTableEntryTypeManager

__all__ = ["NetworkTableClient"]

class ClientConnectionState:
    """Represents a state that the client is in
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

# indicates that the client is disconnected from the server
DISCONNECTED_FROM_SERVER = ClientConnectionState("DISCONNECTED_FROM_SERVER")
# indicates that the client is connected to the server but has not yet begun
# communication
CONNECTED_TO_SERVER = ClientConnectionState("CONNECTED_TO_SERVER")
# represents that the client has sent the hello to the server and is waiting
# for a response
SENT_HELLO_TO_SERVER = ClientConnectionState("SENT_HELLO_TO_SERVER")
# represents that the client is now in sync with the server
IN_SYNC_WITH_SERVER = ClientConnectionState("IN_SYNC_WITH_SERVER")

class ProtocolUnsuppotedByServer(ClientConnectionState):
    """Represents that a client received a message from the server indicating
    that the client's protocol revision is not supported by the server
    """

    def __init__(self, serverVersion):
        """Create a new protocol unsupported state
        :param serverVersion:
        """
        super().__init__("PROTOCOL_UNSUPPORTED_BY_SERVER")
        self.serverVersion = serverVersion

    def getServerVersion(self):
        """:returns: the protocol version that the server reported it supports
        """
        return self.serverVersion

    def __str__(self):
        return "PROTOCOL_UNSUPPORTED_BY_SERVER: Server Version: 0x%x" % self.serverVersion

class ClientError(ClientConnectionState):
    """Represents that the client is in an error state
    """

    def __init__(self, e):
        """Create a new error state
        :param e:
        """
        super().__init__("CLIENT_ERROR")
        self.e = e

    def getException(self):
        """:returns: the exception that caused the client to enter an
            error state
        """
        return self.e

    def __str__(self):
        return "CLIENT_ERROR: %s" % self.e

class ClientConnectionAdapter:
    """Object that adapts messages from a server
    """

    def gotoState(self, newState):
        with self.connectionLock:
            if self.connectionState != newState:
                print("%s entered connection state: %s" % (self, newState))
                if newState == IN_SYNC_WITH_SERVER:
                    self.connectionListenerManager.fireConnectedEvent()
                if self.connectionState == IN_SYNC_WITH_SERVER:
                    self.connectionListenerManager.fireDisconnectedEvent()
                self.connectionState = newState

    def getConnectionState(self):
        """:returns: the state of the connection
        """
        return self.connectionState

    def isConnected(self):
        """:returns: if the client is connected to the server
        """
        return self.connectionState == IN_SYNC_WITH_SERVER

    def __init__(self, entryStore, streamFactory, connectionListenerManager, typeManager):
        """Create a new ClientConnectionAdapter
        :param entryStore:
        :param streamFactory:
        :param transactionPool:
        :param connectionListenerManager:
        """
        self.entryStore = entryStore
        self.streamFactory = streamFactory
        self.connectionListenerManager = connectionListenerManager
        self.typeManager = typeManager
        self.connection = None
        self.readThread = None
        self.connectionState = DISCONNECTED_FROM_SERVER
        self.connectionLock = threading.RLock()

    #
    # Connection management
    #

    def reconnect(self):
        """Reconnect the client to the server (even if the client is not
        currently connected)
        """
        with self.connectionLock:
            self.close() #close the existing stream and monitor thread if needed
            try:
                stream = self.streamFactory.createStream()
                if stream is None:
                    return
                self.connection = NetworkTableConnection(stream, self.typeManager)
                self.readThread = ConnectionMonitorThread(self,
                        self.connection, name="Client Connection Reader Thread")
                readThread.daemon = True
                readThread.start()
                self.connection.sendClientHello()
                self.gotoState(CONNECTED_TO_SERVER)
            except IOError:
                self.close() #make sure to clean everything up if we fail to connect

    def close(self, newState=DISCONNECTED_FROM_SERVER):
        """Close the connection to the server and enter the given state
        :param newState: new state; defaults to DISCONNECTED_FROM_SERVER.
        """
        with self.connectionLock:
            self.gotoState(newState)
            if self.readThread is not None:
                self.readThread.stop()
                self.readThread = None
            if self.connection is not None:
                self.connection.close();
                self.connection = None
            self.entryStore.clearIds()

    def badMessage(self, e):
        self.close(ClientError(e))

    def ioError(self, e):
        if self.connectionState != DISCONNECTED_FROM_SERVER:
            # will get io exception when on read thread connection is closed
            self.reconnect()
        #self.gotoState(ClientError(e))

    def getEntry(self, id):
        return self.entryStore.getEntry(id)

    def keepAlive(self):
        pass

    def clientHello(self, protocolRevision):
        raise BadMessageError("A client should not receive a client hello message")

    def protocolVersionUnsupported(self, protocolRevision):
        self.close()
        self.gotoState(ProtocolUnsuppotedByServer(protocolRevision))

    def serverHelloComplete(self):
        if self.connectionState == CONNECTED_TO_SERVER:
            try:
                self.gotoState(IN_SYNC_WITH_SERVER)
                self.entryStore.sendUnknownEntries(self.connection)
            except IOError as e:
                self.ioException(e)
        else:
            raise BadMessageError("A client should only receive a server hello complete once and only after it has connected to the server")

    def offerIncomingAssignment(self, entry):
        self.entryStore.offerIncomingAssignment(entry)

    def offerIncomingUpdate(self, entry, sequenceNumber, value):
        self.entryStore.offerIncomingUpdate(entry, sequenceNumber, value)

    def offerOutgoingAssignment(self, entry):
        try:
            with self.connectionLock:
                if (self.connection is not None and
                    self.connectionState == IN_SYNC_WITH_SERVER):
                    self.connection.sendEntryAssignment(entry)
        except IOError as e:
            self.ioException(e)

    def offerOutgoingUpdate(self, entry):
        try:
            with self.connectionLock:
                if (self.connection is not None and
                    self.connectionState == IN_SYNC_WITH_SERVER):
                    self.connection.sendEntryUpdate(entry)
        except IOError as e:
            self.ioException(e)

    def flush(self):
        with self.connectionLock:
            if self.connection is not None:
                try:
                    self.connection.flush()
                except IOError as e:
                    self.ioException(e)

    def ensureAlive(self):
        with self.connectionLock:
            if self.connection is not None:
                try:
                    self.connection.sendKeepAlive()
                except IOError as e:
                    self.ioException(e)
            else:
                self.reconnect() #try to reconnect if not connected

class ClientNetworkTableEntryStore(AbstractNetworkTableEntryStore):
    """The entry store for a NetworkTableClient
    """

    def addEntry(self, newEntry):
        with self.mutex:
            entry = self.namedEntries.get(newEntry.name)

            if entry is not None:
                if entry.getId() != newEntry.getId():
                    del self.idEntries[entry.getId()]
                    if newEntry.getId() != NetworkTableEntry.UNKNOWN_ID:
                        entry.setId(newEntry.getId())
                        self.idEntries[newEntry.getId()] = entry

                entry.forcePut(newEntry.getSequenceNumber(),
                               newEntry.getValue(), type=newEntry.getType())
            else:
                if newEntry.getId() != NetworkTableEntry.UNKNOWN_ID:
                    self.idEntries[newEntry.getId()] = newEntry
                self.namedEntries[newEntry.name] = newEntry
        return True

    def updateEntry(self, entry, sequenceNumber, value):
        with self.mutex:
            entry.forcePut(sequenceNumber, value)
            if entry.getId() == NetworkTableEntry.UNKNOWN_ID:
                return False
            return True

    def sendUnknownEntries(self, connection):
        """Send all unknown entries in the entry store to the given connection
        :param connection:
        """
        with self.mutex:
            for entry in self.namedEntries.values():
                if entry.getId() == NetworkTableEntry.UNKNOWN_ID:
                    connection.sendEntryAssignment(entry)
            connection.flush()

class NetworkTableClient(NetworkTableNode):
    """A client node in NetworkTables 2.0
    """

    def __init__(self, streamFactory):
        """Create a new NetworkTable Client
        :param streamFactory:
        """
        super().__init__(ClientNetworkTableEntryStore(self))
        typeManager = NetworkTableEntryTypeManager()
        self.adapter = ClientConnectionAdapter(self.entryStore, streamFactory,
                                               self, typeManager)
        self.writeManager = WriteManager(self.adapter, self.entryStore, 1.0)

        self.entryStore.setOutgoingReceiver(TransactionDirtier(self.writeManager))
        self.entryStore.setIncomingReceiver(None)
        self.writeManager.start()

    def reconnect(self):
        """force the client to disconnect and reconnect to the server again.
        Will connect if the client is currently disconnected
        """
        self.adapter.reconnect()

    def close(self):
        self.adapter.close()

    def stop(self):
        self.writeManager.stop()
        self.close()

    def isConnected(self):
        return self.adapter.isConnected()

    def isServer(self):
        return False
