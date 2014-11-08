import threading
import time

from .common import *
from .connection import *
from .networktablenode import NetworkTableNode
from .stream import StreamEOF
from .type import NetworkTableEntryTypeManager

__all__ = ["NetworkTableServer"]

class ServerConnectionState:
    """Represents the state of a connection to the server
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

# represents that the server has received the connection from the client but
# has not yet received the client hello
GOT_CONNECTION_FROM_CLIENT = ServerConnectionState("GOT_CONNECTION_FROM_CLIENT")
# represents that the client is in a connected non-error state
CONNECTED_TO_CLIENT = ServerConnectionState("CONNECTED_TO_CLIENT")
# represents that the client has disconnected from the server
CLIENT_DISCONNECTED = ServerConnectionState("CLIENT_DISCONNECTED")

class ServerError(ServerConnectionState):
    """Represents that the client is in an error state
    """

    def __init__(self, e):
        """Create a new error state
        :param e:
        """
        super().__init__("SERVER_ERROR")
        self.e = e

    def getException(self):
        """:returns: the exception that caused the client connection to enter
            an error state
        """
        return self.e

    def __str__(self):
        return "SERVER_ERROR: %s" % self.e

class ServerConnectionAdapter:
    """Object that adapts messages from a client to the server
    """

    def gotoState(self, newState):
        if self.connectionState != newState:
            print("%s entered connection state: %s" % (self, newState))
            self.connectionState = newState

    def __init__(self, stream, entryStore, transactionReceiver,
                 adapterListener, typeManager):
        """Create a server connection adapter for a given stream

        :param stream:
        :param entryStore:
        :param transactionReceiver:
        :param adapterListener:
        """
        self.connection = NetworkTableConnection(stream, typeManager)
        self.entryStore = entryStore
        self.transactionReceiver = transactionReceiver
        self.adapterListener = adapterListener

        self.connectionState = None
        self.gotoState(GOT_CONNECTION_FROM_CLIENT)
        self.readThread = ConnectionMonitorThread(self,
                self.connection, name="Server Connection Reader Thread")
        self.readThread.daemon = True
        self.readThread.start()

    def badMessage(self, e):
        self.gotoState(ServerError(e))
        self.adapterListener.close(self, True)

    def ioError(self, e):
        if isinstance(e, StreamEOF):
            self.gotoState(CLIENT_DISCONNECTED);
        else:
            self.gotoState(ServerError(e))
        self.adapterListener.close(self, False)

    def shutdown(self, closeStream):
        """stop the read thread and close the stream
        """
        self.readThread.stop()
        if closeStream:
            self.connection.close()

    def keepAlive(self):
        pass # just let it happen

    def clientHello(self, protocolRevision):
        if self.connectionState != GOT_CONNECTION_FROM_CLIENT:
            raise BadMessageError("A server should not receive a client hello after it has already connected/entered an error state")
        if protocolRevision != NetworkTableConnection.PROTOCOL_REVISION:
            self.connection.sendProtocolVersionUnsupported()
            raise BadMessageError("Client Connected with bad protocol revision: 0x%x" % protocolRevision)
        else:
            self.entryStore.sendServerHello(self.connection)
            self.gotoState(CONNECTED_TO_CLIENT)

    def protocolVersionUnsupported(self, protocolRevision):
        raise BadMessageError("A server should not receive a protocol version unsupported message")

    def serverHelloComplete(self):
        raise BadMessageError("A server should not receive a server hello complete message")

    def offerIncomingAssignment(self, entry):
        self.transactionReceiver.offerIncomingAssignment(entry)

    def offerIncomingUpdate(self, entry, sequenceNumber, value):
        self.transactionReceiver.offerIncomingUpdate(entry, sequenceNumber, value)

    def getEntry(self, id):
        return self.entryStore.getEntry(id)

    def offerOutgoingAssignment(self, entry):
        try:
            if self.connectionState == CONNECTED_TO_CLIENT:
                self.connection.sendEntryAssignment(entry)
        except IOError as e:
            self.ioException(e)

    def offerOutgoingUpdate(self, entry):
        try:
            if self.connectionState == CONNECTED_TO_CLIENT:
                self.connection.sendEntryUpdate(entry)
        except IOError as e:
            self.ioException(e)

    def flush(self):
        try:
            self.connection.flush()
        except IOError as e:
            self.ioException(e)

    def getConnectionState(self):
        """:returns: the state of the connection
        """
        return self.connectionState

    def ensureAlive(self):
        try:
            self.connection.sendKeepAlive()
        except IOError as e:
            self.ioException(e)

class ServerNetworkTableEntryStore(AbstractNetworkTableEntryStore):
    """The entry store for a {@link NetworkTableServer}
    """

    def __init__(self, listenerManager):
        """Create a new Server entry store
        :param listenerManager: the listener manager that fires events from
            this entry store
        """
        super().__init__(listenerManager)
        self.nextId = 0

    def addEntry(self, newEntry):
        with self.mutex:
            entry = self.namedEntries.get(newEntry.name)

            if entry is None:
                newEntry.setId(self.nextId)
                self.nextId += 1
                self.idEntries[newEntry.getId()] = newEntry
                self.namedEntries[newEntry.name] = newEntry
                return True
            return False

    def updateEntry(self, entry, sequenceNumber, value):
        with self.mutex:
            if entry.putValue(sequenceNumber, value):
                return True
            return False

    def sendServerHello(self, connection):
        """Send all entries in the entry store as entry assignments in a
        single transaction
        :param connection:
        """
        with self.mutex:
            for entry in self.namedEntries.values():
                connection.sendEntryAssignment(entry)
            connection.sendServerHelloComplete()
            connection.flush()

class ServerConnectionList:
    """A list of connections that the server currently has
    """

    def __init__(self):
        self.connections = []
        self.connectionsLock = threading.RLock()

    def add(self, connection):
        """Add a connection to the list
        :param connection:
        """
        with self.connectionsLock:
            self.connections.append(connection)

    def close(self, connectionAdapter, closeStream):
        with self.connectionsLock:
            try:
                self.connections.remove(connectionAdapter)
            except ValueError:
                return
            print("Close: %s" % connectionAdapter)
            connectionAdapter.shutdown(closeStream)

    def closeAll(self):
        """close all connections and remove them
        """
        with self.connectionsLock:
            for connection in self.connections:
                print("Close: %s" % connection)
                connection.shutdown(True)
            self.connections.clear()

    def offerOutgoingAssignment(self, entry):
        with self.connectionsLock:
            for connection in self.connections:
                connection.offerOutgoingAssignment(entry)

    def offerOutgoingUpdate(self, entry):
        with self.connectionsLock:
            for connection in self.connections:
                connection.offerOutgoingUpdate(entry)

    def flush(self):
        with self.connectionsLock:
            for connection in self.connections:
                connection.flush()

    def ensureAlive(self):
        with self.connectionsLock:
            for connection in self.connections:
                connection.ensureAlive()

class ServerIncomingStreamMonitor:
    """Thread that monitors for incoming connections
    """

    def __init__(self, streamProvider, entryStore, incomingListener,
                 adapterListener, typeManager):
        """Create a new incoming stream monitor
        :param streamProvider: the stream provider to retrieve streams from
        :param entryStore: the entry store for the server
        :param incomingListener: the listener that is notified of new connections
        :param adapterListener: the listener that will listen to adapter events
        """
        self.streamProvider = streamProvider
        self.entryStore = entryStore
        self.incomingListener = incomingListener
        self.adapterListener = adapterListener
        self.typeManager = typeManager
        self.monitorThread = None
        self.running = False

    def start(self):
        """Start the monitor thread
        """
        if self.monitorThread is not None:
            self.stop()
        self.running = True
        self.monitorThread = threading.Thread(target=self._run,
                                              name="Server Incoming Stream Monitor Thread")
        self.monitorThread.daemon = True
        self.monitorThread.start()

    def stop(self):
        """Stop the monitor thread
        """
        if self.monitorThread is not None:
            self.running = False
            self.monitorThread.join()

    def _run(self):
        while self.running:
            try:
                newStream = self.streamProvider.accept()
                if newStream is not None:
                    connectionAdapter = ServerConnectionAdapter(newStream, self.entryStore, self.entryStore, self.adapterListener, self.typeManager)
                    self.incomingListener.onNewConnection(connectionAdapter)
            except IOError as e:
                pass #could not get a new stream for some reason. ignore and continue

class NetworkTableServer(NetworkTableNode):
    """A server node in NetworkTables 2.0
    """

    def __init__(self, streamProvider):
        """Create a NetworkTable Server
        :param streamProvider:
        """
        super().__init__(ServerNetworkTableEntryStore(self))
        typeManager = NetworkTableEntryTypeManager()
        self.streamProvider = streamProvider

        self.connectionList = ServerConnectionList()
        self.writeManager = WriteManager(self.connectionList, self.entryStore, None)

        self.incomingStreamMonitor = ServerIncomingStreamMonitor(self.streamProvider, self.entryStore, self, self.connectionList, typeManager)

        self.entryStore.setIncomingReceiver(TransactionDirtier(self.writeManager))
        self.entryStore.setOutgoingReceiver(TransactionDirtier(self.writeManager))

        self.incomingStreamMonitor.start()
        self.writeManager.start()

    def close(self):
        try:
            self.incomingStreamMonitor.stop()
            self.writeManager.stop()
            self.connectionList.closeAll()
            time.sleep(1) #To get around bug where an error will occur in select if the socket server is closed before all sockets finish closing
            self.streamProvider.close()
            time.sleep(1)
        except IOError as e:
            print("Error during close: %s" % e)

    def onNewConnection(self, connectionAdapter):
        self.connectionList.add(connectionAdapter)

    def isConnected(self):
        return True

    def isServer(self):
        return True
