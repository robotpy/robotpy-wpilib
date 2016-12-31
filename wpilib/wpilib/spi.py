# validated: 2016-12-20 JW b51e85ae262b athena/java/edu/wpi/first/wpilibj/SPI.java

import hal
import warnings
import weakref

__all__ = ["SPI"]

def _freeSPI(port):
    hal.closeSPI(port)

class SPI:
    """Represents a SPI bus port
    
    Example usage::
    
        spi = wpilib.SPI(wpilib.SPI.Port.kOnboardCS0)
        
        # Write bytes 'text', and receive something
        data = spi.transaction(b'text')
    
    """

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

    def __init__(self, port, simPort=None):
        """Constructor

        :param port: the physical SPI port
        :type port: :class:`.SPI.Port`
        :param simPort: This must be an object that implements all of
                        the spi* functions from hal_impl that you use.
                        See ``test_spi.py`` for an example.
        """
        
        if port not in [self.Port.kOnboardCS0,
                        self.Port.kOnboardCS1,
                        self.Port.kOnboardCS2,
                        self.Port.kOnboardCS3,
                        self.Port.kMXP]:
            raise ValueError("Invalid value '%s' for SPI port" % port)
        
        if hal.HALIsSimulation():
            if simPort is None:
                # If you want more functionality, implement your own mock
                from hal_impl.spi_helpers import SPISimBase
                simPort = SPISimBase()
                
                msg = "Using stub simulator for SPI port %s" % port
                warnings.warn(msg)
            
            # Just check for basic functionality
            assert hasattr(simPort, 'initializeSPI')
            assert hasattr(simPort, 'closeSPI')
            
            self._port = (simPort, port)
        else:
            self._port = port
        
        self.bitOrder = False
        self.clockPolarity = False
        self.dataOnTrailing = False

        hal.initializeSPI(self._port)
        self.__finalizer = weakref.finalize(self, _freeSPI, self._port)

        SPI.devices += 1
        hal.report(hal.UsageReporting.kResourceType_SPI, SPI.devices)
    
    @property
    def port(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use SPI after free() has been called")
        return self._port

    def free(self):
        self.__finalizer()

    def setClockRate(self, hz):
        """Configure the rate of the generated clock signal.
        The default value is 500,000 Hz.
        The maximum value is 4,000,000 Hz.

        :param hz: The clock rate in Hertz.
        """
        hal.setSPISpeed(self.port, hz)

    def setMSBFirst(self):
        """Configure the order that bits are sent and received on the wire
        to be most significant bit first.
        """
        self.bitOrder = True
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setLSBFirst(self):
        """Configure the order that bits are sent and received on the wire
        to be least significant bit first.
        """
        self.bitOrder = False
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setClockActiveLow(self):
        """Configure the clock output line to be active low.
        This is sometimes called clock polarity high or clock idle high.
        """
        self.clockPolarity = True
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setClockActiveHigh(self):
        """Configure the clock output line to be active high.
        This is sometimes called clock polarity low or clock idle low.
        """
        self.clockPolarity = False
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setSampleDataOnFalling(self):
        """Configure that the data is stable on the falling edge and the data
        changes on the rising edge.
        """
        self.dataOnTrailing = True
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setSampleDataOnRising(self):
        """Configure that the data is stable on the rising edge and the data
        changes on the falling edge.
        """
        self.dataOnTrailing = False
        hal.setSPIOpts(self.port, self.bitOrder, self.dataOnTrailing,
                       self.clockPolarity)

    def setChipSelectActiveHigh(self):
        """Configure the chip select line to be active high.
        """
        hal.setSPIChipSelectActiveHigh(self.port)

    def setChipSelectActiveLow(self):
        """Configure the chip select line to be active low.
        """
        hal.setSPIChipSelectActiveLow(self.port)

    def write(self, dataToSend):
        """Write data to the slave device.  Blocks until there is space in the
        output FIFO.

        If not running in output only mode, also saves the data received
        on the MISO input during the transfer into the receive FIFO.

        :param dataToSend: Data to send
        :type dataToSend: iterable of bytes
        
        :returns: Number of bytes written
        
        Usage::
        
            # send byte string
            writeCount = spi.write(b'stuff')
            
            # send list of integers
            writeCount = spi.write([0x01, 0x02])
        """
        return hal.writeSPI(self.port, dataToSend)

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
            return hal.transactionSPI(self.port, [0]*size)
        else:
            return hal.readSPI(self.port, size)

    def transaction(self, dataToSend):
        """Perform a simultaneous read/write transaction with the device

        :param dataToSend: The data to be written out to the device
        :type dataToSend: iterable of bytes

        :returns: data received from the device
        
        Usage::
        
            # send byte string
            data = spi.transaction(b'stuff')
            
            # send list of integers
            data = spi.transaction([0x01, 0x02])
        """
        return hal.transactionSPI(self.port, dataToSend)
    
    
    def initAccumulator(self, period, cmd, xfer_size,
                        valid_mask, valid_value,
                        data_shift, data_size,
                        is_signed, big_endian):
        """Initialize the accumulator.
        
        :param period: Time between reads
        :param cmd: SPI command to send to request data
        :param xfer_size: SPI transfer size, in bytes
        :param valid_mask: Mask to apply to received data for validity checking
        :param valid_data: After valid_mask is applied, required matching value for
                           validity checking
        :param data_shift: Bit shift to apply to received data to get actual data
                           value
        :param data_size: Size (in bits) of data field
        :param is_signed: Is data field signed?
        :param big_endian: Is device big endian?
        """
        hal.initSPIAccumulator(self.port, int(period*1.0e6), cmd,
                               xfer_size, valid_mask, valid_value, data_shift,
                               data_size, is_signed, big_endian)

    def freeAccumulator(self):
        """Frees the accumulator."""
        hal.freeSPIAccumulator(self.port)

    def resetAccumulator(self):
        """Resets the accumulator to zero."""
        hal.resetSPIAccumulator(self.port)

    def setAccumulatorCenter(self, center):
        """Set the center value of the accumulator.
        
        The center value is subtracted from each value before it is added to the accumulator. This
        is used for the center value of devices like gyros and accelerometers to make integration work
        and to take the device offset into account when integrating.
        """
        hal.setSPIAccumulatorCenter(self.port, center)

    def setAccumulatorDeadband(self, deadband):
        """Set the accumulator's deadband."""
        hal.setSPIAccumulatorDeadband(self.port, deadband)

    def getAccumulatorLastValue(self):
        """Read the last value read by the accumulator engine."""

        return hal.getSPIAccumulatorLastValue(self.port);

    def getAccumulatorValue(self):
        """Read the accumulated value.
        
        :returns: The 64-bit value accumulated since the last Reset().
        """
        return hal.getSPIAccumulatorValue(self.port)
    
    def getAccumulatorCount(self):
        """Read the number of accumulated values.
        
        Read the count of the accumulated values since the accumulator was last Reset().
        
        :returns: The number of times samples from the channel were accumulated.
        """
        return hal.getSPIAccumulatorCount(self.port)
    
    def getAccumulatorAverage(self):
        """Read the average of the accumulated value.
        
        :returns: The accumulated average value (value / count).
        """
        return hal.getSPIAccumulatorAverage(self.port)
    
    def getAccumulatorOutput(self):
        """Read the accumulated value and the number of accumulated values atomically.
        
        This function reads the value and count atomically.
        This can be used for averaging.
        
        :returns: tuple of (value, count)
        """
        return hal.getSPIAccumulatorOutput(self.port)    
 
