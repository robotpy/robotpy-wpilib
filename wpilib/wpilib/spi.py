import hal
import weakref

__all__ = ["SPI"]

def _freeSPI(port):
    hal.spiClose(port)

class SPI:
    """Represents a SPI bus port"""

    class Port:
        kOnboardCS0 = 0
        kOnboardCS1 = 1
        kOnboardCS2 = 2
        kOnboardCS3 = 3
        kMXP = 4

    devices = 0
    
    @staticmethod
    def _reset():
        SPI.devices = 0

    def __init__(self, port):
        """Constructor

        :param port: the physical SPI port
        """
        self.port = port
        self.bitOrder = 0
        self.clockPolarity = 0
        self.dataOnTrailing = 0

        hal.spiInitialize(self.port)
        self._spi_finalizer = weakref.finalize(self, _freeSPI, self.port)

        SPI.devices += 1
        hal.HALReport(hal.HALUsageReporting.kResourceType_SPI, SPI.devices)

    def setClockRate(self, hz):
        """Configure the rate of the generated clock signal.
        The default value is 500,000 Hz.
        The maximum value is 4,000,000 Hz.

        :param hz: The clock rate in Hertz.
        """
        hal.spiSetSpeed(self.port, hz)

    def setMSBFirst(self):
        """Configure the order that bits are sent and received on the wire
        to be most significant bit first.
        """
        self.bitOrder = 1
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setLSBFirst(self):
        """Configure the order that bits are sent and received on the wire
        to be least significant bit first.
        """
        self.bitOrder = 0
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setClockActiveLow(self):
        """Configure the clock output line to be active low.
        This is sometimes called clock polarity high or clock idle high.
        """
        self.clockPolarity = 1
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setClockActiveHigh(self):
        """Configure the clock output line to be active high.
        This is sometimes called clock polarity low or clock idle low.
        """
        self.clockPolarity = 0
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setSampleDataOnFalling(self):
        """Configure that the data is stable on the falling edge and the data
        changes on the rising edge.
        """
        self.dataOnTrailing = 1
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setSampleDataOnRising(self):
        """Configure that the data is stable on the rising edge and the data
        changes on the falling edge.
        """
        self.dataOnTrailing = 0
        hal.spiSetOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setChipSelectActiveHigh(self):
        """Configure the chip select line to be active high.
        """
        hal.spiSetChipSelectActiveHigh(self.port)

    def setChipSelectActiveLow(self):
        """Configure the chip select line to be active low.
        """
        hal.spiSetChipSelectActiveLow(self.port)

    def write(self, dataToSend):
        """Write data to the slave device.  Blocks until there is space in the
        output FIFO.

        If not running in output only mode, also saves the data received
        on the MISO input during the transfer into the receive FIFO.

        :param dataToSend: Data to send (bytes)
        """
        hal.spiWrite(self.port, dataToSend)

    def read(self, initiate, size):
        """Read a word from the receive FIFO.

        Waits for the current transfer to complete if the receive FIFO is
        empty.

        If the receive FIFO is empty, there is no active transfer, and
        initiate is False, errors.

        :param initiate: If True, this function pushes "0" into the
            transmit buffer and initiates a transfer.  If False, this function
            assumes that data is already in the receive FIFO from a previous
            write.
        :param size: Number of bytes to read.

        :returns: received data bytes
        """
        if initiate:
            return hal.spiTransaction(self.port, [0]*size)
        else:
            return hal.spiRead(self.port, size)

    def transaction(self, dataToSend):
        """Perform a simultaneous read/write transaction with the device

        :param dataToSend: The data to be written out to the device

        :returns: data received from the device
        """
        return hal.spiTransaction(self.port, dataToSend)
