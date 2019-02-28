import pytest

from hal_impl.spi_helpers import SPISimBase


class SPISimulator(SPISimBase):
    def transactionSPI(self, port, data_to_send, data_received, size):
        assert port == self.port
        assert list(data_to_send) == [1, 2, 3]
        assert size == 3
        data_received[:] = [3, 2, 1]
        self.tx = True
        return 3

    def writeSPI(self, port, data_to_send, send_size):
        assert port == self.port
        assert list(data_to_send) == [5, 6, 7]
        assert send_size == 3
        self.wrote = True
        return 3

    def readSPI(self, port, buffer, count):
        assert port == self.port
        buffer[:] = [9, 9, 0]
        self.did_read = True
        return 3

    def closeSPI(self, port):
        self.closed = True

    def setSPIChipSelectActiveHigh(self, port, status):
        assert port == self.port
        status.value = 0
        self.set_active_high = True

    def setSPIChipSelectActiveLow(self, port, status):
        assert port == self.port
        status.value = 0
        self.set_active_low = True

    def freeSPIAuto(self, port, status):
        status.value = 0
        self.acc_freed = True


def test_spi(wpilib, monkeypatch):

    monkeypatch.setattr(wpilib.Notifier, "_run", lambda s: None)

    sim = SPISimulator()
    port = wpilib.SPI.Port.kMXP

    spi = wpilib.SPI(port, sim)
    assert sim.port == port

    spi.setChipSelectActiveHigh()
    assert sim.set_active_high == True

    spi.setChipSelectActiveLow()
    assert sim.set_active_low == True

    assert spi.transaction([1, 2, 3]) == [3, 2, 1]
    assert sim.tx == True

    assert spi.write([5, 6, 7]) == 3
    assert sim.wrote == True

    assert spi.read(False, 3) == [9, 9, 0]
    assert sim.did_read == True

    spi.freeAccumulator()
    assert sim.acc_freed == True

    # assert spi.getAccumulatorLastValue() == 0x55
    # assert spi.getAccumulatorValue() == 0x66
    # assert spi.getAccumulatorCount() == 0x77
    # assert spi.getAccumulatorAverage() == 0x88
    # assert spi.getAccumulatorOutput() == (0x99, 1)

    spi.close()
    assert sim.closed == True


def test_adxrs450(wpilib, hal_data, monkeypatch, sim_hooks):

    monkeypatch.setattr(wpilib.Notifier, "_run", lambda s: None)

    gyro = wpilib.ADXRS450_Gyro()

    hal_data["robot"]["adxrs450_spi_0_angle"] = 10

    for i in range(10):
        sim_hooks.time = i * 0.1
        assert gyro.getAngle() == pytest.approx(10)

    hal_data["robot"]["adxrs450_spi_0_angle"] = -5
    sim_hooks.time = 2
    assert gyro.getAngle() == pytest.approx(-5)

    # TODO
    # assert gyro.getRate() == pytest.approx(5)
