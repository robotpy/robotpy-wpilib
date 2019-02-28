# validated: 2019-01-04 TW dcbf02a1ecfc edu/wpi/first/wpilibj/SPI.java

import ctypes
import enum

from typing import Tuple, Sequence, Union

import hal
import struct
import threading
import warnings
import weakref

from .accumulatorresult import AccumulatorResult
from .digitalsource import DigitalSource
from .notifier import Notifier

__all__ = ["SPI"]


def _freeSPI(port) -> None:
    hal.closeSPI(port)


class SPI:
    """Represents a SPI bus port

    Example usage::

        spi = wpilib.SPI(wpilib.SPI.Port.kOnboardCS0)

        # Write bytes 'text', and receive something
        data = spi.transaction(b'text')

    """

    class Port(enum.IntEnum):
        kOnboardCS0 = 0
        kOnboardCS1 = 1
        kOnboardCS2 = 2
        kOnboardCS3 = 3
        kMXP = 4

    devices = 0

    @staticmethod
    def _reset() -> None:
        SPI.devices = 0

    def __init__(self, port: Port, simPort=None) -> None:
        """Constructor

        :param port: the physical SPI port
        :param simPort: This must be an object that implements all of
                        the spi* functions from hal_impl that you use.
                        See ``test_spi.py`` for an example.
        """

        port = self.Port(port)

        # python-specific
        if hal.HALIsSimulation():
            if simPort is None:
                # If you want more functionality, implement your own mock
                from hal_impl.spi_helpers import SPISimBase

                simPort = SPISimBase()

                msg = "Using stub simulator for SPI port %s" % port
                warnings.warn(msg)

            # Just check for basic functionality
            assert hasattr(simPort, "initializeSPI")
            assert hasattr(simPort, "closeSPI")

            self.port = (simPort, port)
        else:
            self.port = port

        # python-specific: these are bools instead of integers
        self.msbFirst = False
        self.clockIdleHigh = False
        self.sampleOnTrailing = False

        self.accum = None

        hal.initializeSPI(self.port)
        self.__finalizer = weakref.finalize(self, _freeSPI, self.port)

        SPI.devices += 1
        hal.report(hal.UsageReporting.kResourceType_SPI, SPI.devices)

    def close(self) -> None:
        if self.accum is not None:
            self.accum.close()
            self.accum = None
        self.__finalizer()
        self.port = None

    def setClockRate(self, hz: int) -> None:
        """Configure the rate of the generated clock signal. The default value is 500,000 Hz. The maximum
        value is 4,000,000 Hz.

        :param hz: The clock rate in Hertz.
        """
        hal.setSPISpeed(self.port, hz)

    def setMSBFirst(self) -> None:
        """Configure the order that bits are sent and received on the wire to be most significant bit
        first.
        """
        self.msbFirst = True
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setLSBFirst(self) -> None:
        """Configure the order that bits are sent and received on the wire to be least significant bit
        first.
        """
        self.msbFirst = False
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setClockActiveLow(self) -> None:
        """Configure the clock output line to be active low. This is sometimes called clock polarity high
        or clock idle high.
        """
        self.clockIdleHigh = True
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setClockActiveHigh(self) -> None:
        """Configure the clock output line to be active high. This is sometimes called clock polarity low
        or clock idle low.
        """
        self.clockIdleHigh = False
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setSampleDataOnLeadingEdge(self) -> None:
        """Configure that the data is stable on the leading edge and the data changes on the trailing edge."""
        self.sampleOnTrailing = False
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setSampleDataOnTrailingEdge(self) -> None:
        """Configure that the data is stable on the trailing edge and the data changes on the leading edge."""
        self.sampleOnTrailing = True
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setSampleDataOnFalling(self) -> None:
        """
        Configure that the data is stable on the falling edge and the data changes on the rising edge.
        Note that this gets reversed if setClockActiveLow is set

        .. deprecated:: 2019.0.0
            Use setSampleDataOnTrailingEdge in most cases
        """
        self.sampleOnTrailing = True
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setSampleDataOnRising(self) -> None:
        """
        Configure that the data is stable on the rising edge and the data changes on the falling edge.

        .. deprecated:: 2019.0.0
            Use setSampleDataOnLeadingEdge in most cases
        """
        self.sampleOnTrailing = False
        hal.setSPIOpts(
            self.port, self.msbFirst, self.sampleOnTrailing, self.clockIdleHigh
        )

    def setChipSelectActiveHigh(self) -> None:
        """Configure the chip select line to be active high."""
        hal.setSPIChipSelectActiveHigh(self.port)

    def setChipSelectActiveLow(self) -> None:
        """Configure the chip select line to be active low."""
        hal.setSPIChipSelectActiveLow(self.port)

    def write(self, dataToSend: Union[bytes, Sequence[int]]) -> int:
        """Write data to the slave device.  Blocks until there is space in the
        output FIFO.

        If not running in output only mode, also saves the data received
        on the MISO input during the transfer into the receive FIFO.

        :param dataToSend: Data to send

        :returns: Number of bytes written

        Usage::

            # send byte string
            writeCount = spi.write(b'stuff')

            # send list of integers
            writeCount = spi.write([0x01, 0x02])
        """
        return hal.writeSPI(self.port, dataToSend)

    def read(self, initiate: bool, size: int) -> bytes:
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
            return hal.transactionSPI(self.port, [0] * size)
        else:
            return hal.readSPI(self.port, size)

    def transaction(self, dataToSend: Union[bytes, Sequence[int]]) -> bytes:
        """Perform a simultaneous read/write transaction with the device

        :param dataToSend: The data to be written out to the device

        :returns: data received from the device

        Usage::

            # send byte string
            data = spi.transaction(b'stuff')

            # send list of integers
            data = spi.transaction([0x01, 0x02])
        """
        return hal.transactionSPI(self.port, dataToSend)

    def initAuto(self, bufferSize: int) -> None:
        """Initialize automatic SPI transfer engine.

        Only a single engine is available, and use of it blocks use of all other
        chip select usage on the same physical SPI port while it is running.

        :param bufferSize: buffer size in bytes
        """
        hal.initSPIAuto(self.port, bufferSize)

    def freeAuto(self) -> None:
        """Frees the automatic SPI transfer engine."""
        hal.freeSPIAuto(self.port)

    def setAutoTransmitData(self, dataToSend: bytes, zeroSize: int) -> None:
        """Set the data to be transmitted by the engine.

        Up to 16 bytes are configurable, and may be followed by up to 127 zero
        bytes.

        :param dataToSend: data to send (maximum 16 bytes)
        :param zeroSize: number of zeros to send after the data
        """
        hal.setSPIAutoTransmitData(self.port, dataToSend, zeroSize)

    def startAutoRate(self, period: float) -> None:
        """Start running the automatic SPI transfer engine at a periodic rate.

        :meth:`.initAuto` and :meth:`.setAutoTransmitData` must
        be called before calling this function.

        :param period: period between transfers, in seconds (us resolution)
        """
        hal.startSPIAutoRate(self.port, period)

    def startAutoTrigger(
        self, source: DigitalSource, rising: bool, falling: bool
    ) -> None:
        """Start running the automatic SPI transfer engine when a trigger occurs.

        :meth:`.initAuto` and :meth:`.setAutoTransmitData` must
        be called before calling this function.

        :param source: digital source for the trigger (may be an analog trigger)
        :param rising: trigger on the rising edge
        :param falling: trigger on the falling edge
        """
        hal.startSPIAutoTrigger(
            self.port,
            source.getPortHandleForRouting(),
            source.getAnalogTriggerTypeForRouting(),
            rising,
            falling,
        )

    def stopAuto(self) -> None:
        """Stop running the automatic SPI transfer engine."""
        hal.stopSPIAuto(self.port)

    def forceAutoRead(self) -> None:
        """Force the engine to make a single transfer."""
        hal.forceSPIAutoRead(self.port)

    def readAutoReceivedData(
        self, buffer: bytes, numToRead: int, timeout: float
    ) -> Tuple[int, bytes]:
        """Read data that has been transferred by the automatic SPI transfer engine.

        Transfers may be made a byte at a time, so it's necessary for the caller
        to handle cases where an entire transfer has not been completed.

        Each received data sequence consists of a timestamp followed by the
        received data bytes, one byte per word (in the least significant byte).
        The length of each received data sequence is the same as the combined
        size of the data and zeroSize set in setAutoTransmitData().

        Blocks until numToRead words have been read or timeout expires.
        May be called with numToRead=0 to retrieve how many words are available.

        :param buffer:    A ctypes c_uint32 buffer to read the data into
        :param numToRead: number of words to read
        :param timeout:   timeout in seconds (ms resolution)
        
        :returns: Number of words remaining to be read
        """
        if len(buffer) < numToRead:
            raise ValueError("buffer is too small, must be at least %s" % numToRead)
        return hal.readSPIAutoReceivedData(self.port, buffer, numToRead, timeout)

    def getAutoDroppedCount(self) -> int:
        """Get the number of bytes dropped by the automatic SPI transfer engine due
        to the receive buffer being full.

        :returns: Number of bytes dropped
        """
        return hal.getSPIAutoDroppedCount(self.port)

    class _Accumulator:

        kAccumulateDepth = 2048

        def __init__(
            self,
            port: int,
            xferSize: int,
            validMask: int,
            validValue: int,
            dataShift: int,
            dataSize: int,
            isSigned: bool,
            bigEndian: bool,
        ) -> None:
            self._mutex = threading.RLock()
            self._notifier = Notifier(self._update)
            self._buf = (ctypes.c_uint32 * (xferSize * self.kAccumulateDepth))()

            # fmt: off
            self._xferSize = xferSize + 1               # +1 for timestamp
            self._validMask = validMask
            self._validValue = validValue
            self._dataShift = dataShift                 # data field shift right amount, in bits
            self._dataMax = 1 << dataSize               # one more than max data value
            self._dataMsbMask = 1 << (dataSize - 1)     # data field MSB mask (for signed)
            self._isSigned = isSigned                   # is data field signed?
            self._bigEndian = bigEndian                 # is response big endian?
            self._port = port
            # fmt: on

            self._value = 0
            self._count = 0
            self._lastValue = 0
            self._lastTimestamp = 0
            self._integratedValue = 0.0

            self._center = 0
            self._deadband = 0
            self._integratedCenter = 0.0

        def free(self) -> None:
            """
            .. deprecated:: 2019.0.0
                Use close instead
            """
            warnings.warn("use close instead", DeprecationWarning, stacklevel=2)
            self.close()

        def close(self):
            self._notifier.close()

        def _update(self) -> None:
            with self._mutex:
                done = False
                while not done:
                    done = True

                    # get amount of data available
                    numToRead = hal.readSPIAutoReceivedData(self._port, self._buf, 0, 0)

                    # only get whole responses
                    numToRead -= numToRead % self._xferSize
                    if numToRead > self._xferSize * self.kAccumulateDepth:
                        numToRead = self._xferSize * self.kAccumulateDepth
                        done = False

                    if numToRead == 0:
                        return  # no samples

                    # read buffered data
                    hal.readSPIAutoReceivedData(self._port, self._buf, numToRead, 0)

                    # loop over all responses
                    for off in range(0, numToRead, self._xferSize):
                        # get timestamp from first word
                        timestamp = self._buf[off] & 0xFFFFFFFF

                        # convert from bytes
                        resp = 0
                        if self._bigEndian:
                            for i in range(1, self._xferSize):
                                resp <<= 8
                                resp |= self._buf[off + i] & 0xFF
                        else:
                            for i in range(self._xferSize - 1, 0):
                                resp <<= 8
                                resp |= self._buf[off + i] & 0xFF

                        # process response
                        if (resp & self._validMask) == self._validValue:

                            # valid sensor data extract data field
                            data = resp >> self._dataShift
                            data &= self._dataMax - 1

                            # 2s complement conversion if signed MSB is set
                            if self._isSigned and (data & self._dataMsbMask) != 0:
                                data -= self._dataMax

                            # center offset
                            dataNoCenter = data
                            data -= self._center

                            # only accumulate if outside deadband
                            if data < -self._deadband or data > self._deadband:
                                self._value += data
                                if self._count != 0:
                                    # timestamps use the 1us FPGA clock; also handle rollover
                                    if timestamp >= self._lastTimestamp:
                                        self._integratedValue = (
                                            dataNoCenter
                                            * (timestamp - self._lastTimestamp)
                                            * 1e-6
                                            - self._integratedCenter
                                        )
                                    else:
                                        self._integratedValue += (
                                            dataNoCenter
                                            * (
                                                (1 << 32)
                                                - self._lastTimestamp
                                                + timestamp
                                            )
                                            * 1e-6
                                            - self._integratedCenter
                                        )

                            self._count += 1
                            self._lastValue = data
                        else:
                            # no data from the sensor just clear the last value
                            self._lastValue = 0

                        self._lastTimestamp = timestamp

    def initAccumulator(
        self,
        period: float,
        cmd: int,
        xferSize: int,
        validMask: int,
        validValue: int,
        dataShift: int,
        dataSize: int,
        isSigned: bool,
        bigEndian: bool,
    ) -> None:
        """Initialize the accumulator.

        :param period: Time between reads
        :param cmd: SPI command to send to request data
        :param xferSize: SPI transfer size, in bytes
        :param validMask: Mask to apply to received data for validity checking
        :param validValue: After validMask is applied, required matching value for validity checking
        :param dataShift: Bit shift to apply to received data to get actual data value
        :param dataSize: Size (in bits) of data field
        :param isSigned: Is data field signed?
        :param bigEndian: Is device big endian?
        """
        self.initAuto(xferSize * 2048)

        if bigEndian:
            cmdBytes = cmd.to_bytes(4, "big")
        else:
            cmdBytes = cmd.to_bytes(4, "little")

        self.setAutoTransmitData(cmdBytes, xferSize - 4)
        self.startAutoRate(period)

        self.accum = self._Accumulator(
            self.port,
            xferSize,
            validMask,
            validValue,
            dataShift,
            dataSize,
            isSigned,
            bigEndian,
        )
        self.accum._notifier.startPeriodic(period * 1024)

    def freeAccumulator(self) -> None:
        """Frees the accumulator."""
        if self.accum:
            self.accum.close()
            self.accum = None
        self.freeAuto()

    def resetAccumulator(self) -> None:
        """Resets the accumulator to zero."""
        if not self.accum:
            return
        with self.accum._mutex:
            self.accum._value = 0
            self.accum._count = 0
            self.accum._lastValue = 0
            self.accum._lastTimestamp = 0
            self.accum._integratedValue = 0.0

    def setAccumulatorCenter(self, center: int) -> None:
        """Set the center value of the accumulator.

        The center value is subtracted from each value before it is added to the accumulator. This
        is used for the center value of devices like gyros and accelerometers to make integration work
        and to take the device offset into account when integrating.
        """
        if not self.accum:
            return
        with self.accum._mutex:
            self.accum._center = center

    def setAccumulatorDeadband(self, deadband: int) -> None:
        """Set the accumulator's deadband."""
        if not self.accum:
            return
        with self.accum._mutex:
            self.accum._deadband = deadband

    def getAccumulatorLastValue(self) -> int:
        """Read the last value read by the accumulator engine."""
        if not self.accum:
            return 0
        with self.accum._mutex:
            self.accum._update()
            return self.accum._lastValue

    def getAccumulatorValue(self) -> int:
        """Read the accumulated value.

        :returns: The 64-bit value accumulated since the last Reset().
        """
        if not self.accum:
            return 0
        with self.accum._mutex:
            self.accum._update()
            return self.accum._value

    def getAccumulatorCount(self) -> int:
        """Read the number of accumulated values.

        Read the count of the accumulated values since the accumulator was last Reset().

        :returns: The number of times samples from the channel were accumulated.
        """
        if not self.accum:
            return 0
        with self.accum._mutex:
            self.accum._update()
            return self.accum._count

    def getAccumulatorAverage(self) -> float:
        """Read the average of the accumulated value.

        :returns: The accumulated average value (value / count).
        """
        if not self.accum:
            return 0
        with self.accum._mutex:
            self.accum._update()
            if self.accum._count == 0:
                return 0.0
            else:
                return float(self.accum._value) / self.accum._count

    def getAccumulatorOutput(self) -> AccumulatorResult:
        """Read the accumulated value and the number of accumulated values atomically.

        This function reads the value and count atomically.
        This can be used for averaging.

        :returns: tuple of (value, count)
        """
        if self.accum is None:
            return AccumulatorResult(0, 0)

        with self.accum._mutex:
            self.accum._update()
            return AccumulatorResult(self.accum._value, self.accum._count)

    def setAccumulatorIntegratedCenter(self, center: float) -> None:
        """Set the center value of the accumulator integrator.

        The center value is subtracted from each value*dt before it is added to the
        integrated value. This is used for the center value of devices like gyros
        and accelerometers to take the device offset into account when integrating.

        """
        if self.accum is None:
            return

        with self.accum._mutex:
            self.accum._integratedCenter = center

    def getAccumulatorIntegratedValue(self) -> float:
        """Read the integrated value.  This is the sum of (each value * time between
        values).

        :returns: The integrated value accumulated since the last Reset().
        """
        if self.accum is None:
            return

        with self.accum._mutex:
            self.accum._update()
            return self.accum._integratedValue

    def getAccumulatorIntegratedAverage(self) -> float:
        """Read the average of the integrated value.  This is the sum of (each value
        times the time between values), divided by the count.

        :returns: The average of the integrated value accumulated since the last Reset().
        """
        if self.accum is None:
            return 0.0

        with self.accum._mutex:
            self.accum._update()
            if self.accum._count <= 1:
                return 0.0

            # count-1 due to not integrating the first value received
            return self.accum._integratedValue / (self.accum._count - 1)
