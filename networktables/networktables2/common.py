# Common classes for client and server

import threading
import time
import warnings

from .networktableentry import NetworkTableEntry

__all__ = ["AbstractNetworkTableEntryStore", "TransactionDirtier",
           "WriteManager"]

class AbstractNetworkTableEntryStore:
    """An entry store that handles storing entries and applying transactions
    """

    def __init__(self, listenerManager):
        self.idEntries = {}
        self.namedEntries = {}
        self.listenerManager = listenerManager
        self.outgoingReceiver = None
        self.incomingReceiver = None
        self.mutex = threading.RLock()

    def getEntry(self, name_id):
        """Get an entry based on its name or id
        :param name_id: the name or id of the entry to look for
        :returns: the entry or None if the entry does not exist
        """
        with self.mutex:
            if isinstance(name_id, str):
                return self.namedEntries.get(name_id)
            else:
                return self.idEntries.get(name_id)

    def keys(self):
        """Get the list of keys.
        :returns: the list of keys
        """
        with self.mutex:
            return self.namedEntries.keys().copy()

    def clearEntries(self):
        """Remove all entries.
        NOTE: This method should not be used with applications which cache
        entries which would lead to unknown results.
        This method is for use in testing only.
        """
        with self.mutex:
            self.idEntries.clear()
            self.namedEntries.clear()

    def clearIds(self):
        """clear the id's of all entries
        """
        with self.mutex:
            self.idEntries.clear()
            for entry in self.namedEntries.values():
                entry.clearId()

    def setOutgoingReceiver(self, receiver):
        self.outgoingReceiver = receiver

    def setIncomingReceiver(self, receiver):
        self.incomingReceiver = receiver

    def addEntry(self, entry):
        raise NotImplementedError

    def updateEntry(self, entry, sequenceNumber, value):
        raise NotImplementedError

    def putOutgoing(self, name, type, value):
        """Stores the given value under the given name and queues it for
        transmission to the server.

        :param name: The name under which to store the given value.
        :param type: The type of the given value.
        :param value: The value to store.
        Raises TypeError if entry already exists with the given name and is of
        a different type.
        """
        with self.mutex:
            tableEntry = self.namedEntries.get(name)
            if tableEntry is None:
                #TODO validate type
                tableEntry = NetworkTableEntry(name, type, value)
                if self.addEntry(tableEntry):
                    tableEntry.fireListener(self.listenerManager)
                    if self.outgoingReceiver is not None:
                        self.outgoingReceiver.offerOutgoingAssignment(tableEntry)
            else:
                if tableEntry.getType().id != type.id:
                    raise TypeError(name)
                if value != tableEntry.getValue():
                    if self.updateEntry(tableEntry, tableEntry.getSequenceNumber()+1, value):
                        if self.outgoingReceiver is not None:
                            self.outgoingReceiver.offerOutgoingUpdate(tableEntry)
                    tableEntry.fireListener(self.listenerManager)

    def putOutgoingEntry(self, tableEntry, value):
        with self.mutex:
            #TODO Validate type
            if value != tableEntry.getValue():
                if self.updateEntry(tableEntry, tableEntry.getSequenceNumber()+1, value):
                    if self.outgoingReceiver is not None:
                        self.outgoingReceiver.offerOutgoingUpdate(tableEntry)
                tableEntry.fireListener(self.listenerManager)

    def offerIncomingAssignment(self, entry):
        with self.mutex:
            tableEntry = self.namedEntries.get(entry.name)
            if self.addEntry(entry):
                if tableEntry is None:
                    tableEntry = entry
                tableEntry.fireListener(self.listenerManager)
                if self.incomingReceiver is not None:
                    self.incomingReceiver.offerOutgoingAssignment(tableEntry)

    def offerIncomingUpdate(self, entry, sequenceNumber, value):
        with self.mutex:
            if self.updateEntry(entry, sequenceNumber, value):
                entry.fireListener(self.listenerManager)
                if self.incomingReceiver is not None:
                    self.incomingReceiver.offerOutgoingUpdate(entry)

    def notifyEntries(self, table, listener):
        """Called to say that a listener should notify the listener manager
        of all of the entries
        :param listener:
        :param table:
        """
        with self.mutex:
            while entry in self.namedEntries.values():
                listener.valueChanged(table, entry.name, entry.getValue(), True)

class TransactionDirtier:
    """A transaction receiver that marks all Table entries as dirty in the
    entry store. Entries will not be passed to the continuing receiver if
    they are already dirty
    """

    def __init__(self, continuingReceiver):
        self.continuingReceiver = continuingReceiver

    def offerOutgoingAssignment(self, entry):
        if entry.isDirty:
            return
        entry.makeDirty()
        self.continuingReceiver.offerOutgoingAssignment(entry)

    def offerOutgoingUpdate(self, entry):
        if entry.isDirty:
            return
        entry.makeDirty()
        self.continuingReceiver.offerOutgoingUpdate(entry)

class WriteManager:
    """A write manager is a IncomingEntryReceiver that buffers transactions
    and then and then dispatches them to a flushable transaction receiver
    that is periodically offered all queued transaction and then flushed
    """
    SLEEP_TIME = 0.1
    queueSize = 500

    def __init__(self, receiver, entryStore, keepAliveDelay):
        """Create a new Write manager
        :param receiver:
        :param transactionPool:
        :param entryStore:
        """
        self.receiver = receiver
        self.entryStore = entryStore
        self.keepAliveDelay = keepAliveDelay
        self.lastWrite = 0

        self.transactionsLock = threading.RLock()

        self.incomingAssignmentQueue = []
        self.incomingUpdateQueue = []
        self.outgoingAssignmentQueue = []
        self.outgoingUpdateQueue = []

        self.thread = None
        self.running = False

    def start(self):
        """start the write thread
        """
        if self.thread is not None:
            self.stop()
        self.lastWrite = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._runPeriodic,
                                       name="Write Manager Thread")
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """stop the write thread
        """
        if self.thread is not None:
            self.running = False
            self.thread.join()

    def offerOutgoingAssignment(self, entry):
        with self.transactionsLock:
            self.incomingAssignmentQueue.append(entry)
            if len(self.incomingAssignmentQueue) >= self.queueSize:
                self.run()
                warnings.warn("assignment queue overflowed. decrease the rate at which you create new entries or increase the write buffer size", ResourceWarning)

    def offerOutgoingUpdate(self, entry):
        with self.transactionsLock:
            self.incomingUpdateQueue.append(entry)
            if len(self.incomingUpdateQueue) >= self.queueSize:
                self.run()
                warnings.warn("update queue overflowed. decrease the rate at which you update entries or increase the write buffer size", ResourceWarning)

    def _runPeriodic(self):
        while self.running:
            self.run()
            time.sleep(self.SLEEP_TIME)

    def run(self):
        """the periodic method that sends all buffered transactions
        """
        with self.transactionsLock:
            #swap the assignment and update queue
            self.incomingAssignmentQueue, self.outgoingAssignmentQueue = \
                self.outgoingAssignmentQueue, self.incomingAssignmentQueue

            self.incomingUpdateQueue, self.outgoingUpdateQueue = \
                self.outgoingUpdateQueue, self.incomingUpdateQueue

        wrote = False
        for entry in self.outgoingAssignmentQueue:
            with self.entryStore.mutex:
                entry.makeClean()
            wrote = True
            if self.receiver is not None:
                self.receiver.offerOutgoingAssignment(entry)
        self.outgoingAssignmentQueue.clear()

        for entry in self.outgoingUpdateQueue:
            with self.entryStore.mutex:
                entry.makeClean()
            wrote = True
            if self.receiver is not None:
                self.receiver.offerOutgoingUpdate(entry)
        self.outgoingUpdateQueue.clear()

        if wrote:
            if self.receiver is not None:
                self.receiver.flush()
            self.lastWrite = time.time()
        elif (self.keepAliveDelay is not None and
              (time.time()-self.lastWrite) > self.keepAliveDelay):
            if self.receiver is not None:
                self.receiver.ensureAlive()
