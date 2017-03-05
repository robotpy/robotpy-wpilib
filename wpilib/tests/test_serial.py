
import pytest

import hal
from hal_impl.serial_helpers import SerialSimBase

class SerialSimulator(SerialSimBase):
    pass

    # TODO: expand this

def test_serial(wpilib):
    simPort = SerialSimulator()
    
    serial = wpilib.SerialPort(9600, wpilib.SerialPort.Port.kOnboard, simPort=simPort)
    
    # TODO: expand the tests
    serial.write(b'some bytes')
    