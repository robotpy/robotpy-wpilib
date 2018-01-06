# validated: 2018-01-06 DS 479d0beb5a79 edu/wpi/first/wpilibj/SerialPort.java
#----------------------------------------------------------------------------
# Copyright (c) FIRST 2008-2017. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import hal
import warnings
import weakref

from .resource import Resource

__all__ = ['SerialPort']

import logging
logger = logging.getLogger(__name__)

def _freeSerialPort(port):
    hal.closeSerial(port)

class SerialPort:
    """
        Driver for the RS-232 serial port on the roboRIO.
        
        The current implementation uses the VISA formatted I/O mode. This means that all traffic goes
        through the formatted buffers. This allows the intermingled use of print(), readString(), and the
        raw buffer accessors read() and write().
        
        More information can be found in the NI-VISA User Manual here:
        http://www.ni.com/pdf/manuals/370423a.pdf
        
        and the NI-VISA Programmer's Reference Manual here:
        http://www.ni.com/pdf/manuals/370132c.pdf
    """
    
    class Port:
        kOnboard = 0
        kMXP = 1
        kUSB = 2
        kUSB1 = 2
        kUSB2 = 3
            
    class Parity:
        kNone = 0
        kOdd = 1
        kEven = 2
        kMark = 3
        kSpace = 4
            
    class StopBits:
        kOne = 10
        kOnePointFive = 15
        kTwo = 20
            
    class FlowControl:
        kNone = 0
        kXonXoff = 1
        kRtsCts = 2
        kDtsDsr = 4
            
    class WriteBufferMode:
        kFlushOnAccess = 1
        kFlushWhenFull = 2
    
    
    def __init__(self, baudRate, port, dataBits=8,
                 parity=Parity.kNone,
                 stopBits=StopBits.kOne,
                 simPort=None):
        """Create an instance of a Serial Port class.
        
        :param baudRate: The baud rate to configure the serial port.
        :param port: The Serial port to use
        :param dataBits: The number of data bits per transfer. Valid values are between 5 and 8 bits.
        :param parity: Select the type of parity checking to use.
        :param stopBits: The number of stop bits to use as defined by the enum StopBits.
        :param simPort: This must be an object that implements all of
                        the serial* functions from hal_impl that you use.
                        See ``test_serial.py`` for an example.
        """
    
        if port not in [self.Port.kOnboard,
                        self.Port.kMXP,
                        self.Port.kUSB,
                        self.Port.kUSB1,
                        self.Port.kUSB2]:
            raise ValueError("Invalid value '%s' for serial port" % port)
        
        if hal.isSimulation():
            if simPort is None:
                # If you want more functionality, implement your own mock
                from hal_impl.serial_helpers import SerialSimBase
                simPort = SerialSimBase()
                
                msg = "Using stub simulator for Serial port %s" % port
                warnings.warn(msg)
        
            self._port = (simPort, port)
        else:
            self._port = port
        
        hal.initializeSerialPort(self._port)
        self.__finalizer = weakref.finalize(self, _freeSerialPort, self._port)
        
        hal.setSerialBaudRate(self.port, baudRate)
        hal.setSerialDataBits(self.port, dataBits)
        hal.setSerialParity(self.port, parity)
        hal.setSerialStopBits(self.port, stopBits)

        # Set the default read buffer size to 1 to return bytes immediately
        self.setReadBufferSize(1)

        # Set the default timeout to 5 seconds.
        self.setTimeout(5.0)

        # Don't wait until the buffer is full to transmit.
        self.setWriteBufferMode(self.WriteBufferMode.kFlushOnAccess)

        self.disableTermination()

        hal.report(hal.UsageReporting.kResourceType_SerialPort, 0)
        
        # Need this to free on unit test wpilib reset
        Resource._add_global_resource(self)

    @property
    def port(self):
        if not self.__finalizer.alive:
            raise ValueError("Cannot use serial port after free() has been called")
        return self._port
    
    def free(self):
        '''Destructor'''
        self._finalizer()

    def setFlowControl(self, flowControl):
        """Set the type of flow control to enable on this port.
        
        By default, flow control is disabled.
        
        :param flowControl: the FlowControl value to use
        """
        hal.setSerialFlowControl(self.port, flowControl)
    
    def enableTermination(self, terminator=b'\n'):
        """Enable termination and specify the termination character.
        
        Termination is currently only implemented for receive. When the the terminator is received,
        the :meth:`read` or :meth:`readString` will return fewer bytes than requested, stopping after the
        terminator.
        
        :param terminator: The character to use for termination (default is ``\\n``).
        """
        hal.enableSerialTermination(self.port, terminator)
    
    def disableTermination(self):
        """Disable termination behavior."""
        hal.disableSerialTermination(self.port)
    
    def getBytesReceived(self):
        """Get the number of bytes currently available to read from the serial port.
        
        :returns: The number of bytes available to read.
        """
        return hal.getSerialBytesReceived(self.port)
    
    def readString(self, count=None):
        """Read a string out of the buffer. Reads the entire contents of the buffer
        
        :param count: the number of characters to read into the string
        :returns: The read string
        """
        if count is None:
            count = self.getBytesReceived()
        
        try:
            return self.read(count).decode('ascii')
        except UnicodeDecodeError:
            logger.warning("Error decoding serial port output")
            return ''
    
    def read(self, count):
        """Read raw bytes out of the buffer.
        
        :param count: The maximum number of bytes to read.
        :returns: A list containing the read bytes
        """
        return hal.readSerial(self.port, count)
    
    def write(self, buffer):
        """Write raw bytes to the serial port.
        
        :param buffer: The buffer of bytes to write.
        :param count: The maximum number of bytes to write.
        :returns: The number of bytes actually written into the port.
        """
        return hal.writeSerial(self.port, buffer)
    
    def writeString(self, data):
        """Write an ASCII encoded string to the serial port
        
        :param data: The string to write to the serial port.
        :returns: The number of bytes actually written into the port.
        """
        return self.write(data.encode('ascii'))
    
    def setTimeout(self, timeout):
        """Configure the timeout of the serial self.port.
        
        This defines the timeout for transactions with the hardware. It will affect reads if less
        bytes are available than the read buffer size (defaults to 1) and very large writes.
        
        :param timeout: The number of seconds to to wait for I/O.
        """
        hal.setSerialTimeout(self.port, timeout)
    
    def setReadBufferSize(self, size):
        """Specify the size of the input buffer.
        
        Specify the amount of data that can be stored before data from the device is returned to
        Read. If you want data that is received to be returned immediately, set this to 1.
        
        It the buffer is not filled before the read timeout expires, all data that has been received
        so far will be returned.
        
        :param size: The read buffer size.
        """
        hal.setSerialReadBufferSize(self.port, size)
    
    def setWriteBufferSize(self, size):
        """Specify the size of the output buffer.
        
        Specify the amount of data that can be stored before being transmitted to the device.
        
        :param size: The write buffer size.
        """
        hal.setSerialWriteBufferSize(self.port, size)
    
    def setWriteBufferMode(self, mode):
        """Specify the flushing behavior of the output buffer.
        
        When set to kFlushOnAccess, data is synchronously written to the serial port after each
        call to either print() or write().
        
        When set to kFlushWhenFull, data will only be written to the serial port when the buffer
        is full or when flush() is called.
        
        :param mode: The write buffer mode.
        :type mode: WriteBufferMode
        """
        hal.setSerialWriteMode(self.port, mode)
    
    def flush(self):
        """Force the output buffer to be written to the port.
        
        This is used when :meth:`setWriteBufferMode` is set to kFlushWhenFull to force a flush before the
        buffer is full.
        """
        hal.flushSerial(self.port)
    
    def reset(self):
        """Reset the serial port driver to a known state.
        
        Empty the transmit and receive buffers in the device and formatted I/O.
        """
        hal.clearSerial(self.port)

