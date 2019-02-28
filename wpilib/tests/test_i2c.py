import pytest

import hal
from hal_impl.i2c_helpers import I2CSimBase


class I2CSimulator(I2CSimBase):
    """
        An object similar to this can be passed to the I2C constructor as
        'simPort' and it will get called when I2C HAL calls are made
    """

    def transactionI2C(
        self, port, device_address, data_to_send, send_size, data_received, receive_size
    ):
        assert device_address == 0x42
        assert list(data_to_send) == [1, 2]
        data_received[:] = [2, 1]
        return 2

    def writeI2C(self, port, device_address, data_to_send, send_size):
        assert device_address == 0x42

        if data_to_send[0] == 3:
            assert list(data_to_send) == [3, 4]
            self.written = True
        else:  # bulk
            assert list(data_to_send) == [5, 6, 7]
            self.bulkWritten = True

        return 1

    def readI2C(self, port, device_address, buffer, count):
        assert device_address == 0x42
        buffer[:] = [0x24] * count
        return count

    def closeI2C(self, port):
        self.closed = port


def test_i2c(hal, wpilib):

    sim = I2CSimulator()
    port = wpilib.I2C.Port.kMXP

    i2c = wpilib.I2C(port, 0x42, sim)
    assert sim.port == port

    assert i2c.transaction([1, 2], 2) == [2, 1]

    print(i2c.write(3, 4))
    assert i2c.write(3, 4) == False
    assert sim.written is True

    assert i2c.writeBulk([5, 6, 7]) == False
    assert sim.bulkWritten is True

    assert i2c.readOnly(7) == [0x24] * 7

    # TODO: test verifySensor

    i2c.close()
    assert sim.closed == port

    with pytest.raises(hal.HALError):
        i2c.readOnly(7)
