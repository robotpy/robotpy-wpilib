
import pytest

class SPISimulator:
    
    def spiInitialize(self, port, status):
        self.port = port
        status.value = 0
        self.initialized = port
    
    def spiTransaction(self, port, data_to_send, data_received, size):
        assert port == self.port
        assert list(data_to_send) == [1, 2, 3]
        assert size == 3
        data_received[:] = [3,2,1]
        self.tx = True
        return 3
    
    def spiWrite(self, port, data_to_send, send_size):
        assert port == self.port
        assert list(data_to_send) == [5,6,7]
        assert send_size == 3
        self.wrote = True
        return 3
    
    def spiRead(self, port, buffer, count):
        assert port == self.port
        buffer[:] = [9, 9, 0]
        self.did_read = True
        return 3
    
    def spiClose(self, port):
        self.closed = True
    
    def spiSetSpeed(self, port, speed):
        assert False
    
    def spiSetOpts(self, port, msb_first, sample_on_trailing, clk_idle_high):
        assert False
    
    def spiSetChipSelectActiveHigh(self, port, status):
        assert port == self.port
        status.value = 0
        self.set_active_high = True
    
    def spiSetChipSelectActiveLow(self, port, status):
        assert port == self.port
        status.value = 0
        self.set_active_low = True
    
    def spiGetHandle(self, port):
        assert False
    
    def spiSetHandle(self, port, handle):
        assert False
        
    def spiInitAccumulator(self, port,
                           period, cmd, xfer_size, valid_mask, valid_value,
                           data_shift, data_size, is_signed, big_endian, status):
        assert False
        
    def spiFreeAccumulator(self, port, status):
        status.value = 0
        self.acc_freed = True
        
    def spiResetAccumulator(self, port, status):
        status.value = 0
        self.acc_reset = True
    
    def spiSetAccumulatorCenter(self, port, center, status):
        assert False
        
    def spiSetAccumulatorDeadband(self, port, deadband, status):
        assert False
        
    def spiGetAccumulatorLastValue(self, port, status):
        assert port == self.port
        status.value = 0
        return 0x55
        
    def spiGetAccumulatorValue(self, port, status):
        assert port == self.port
        status.value = 0
        return 0x66
        
    def spiGetAccumulatorCount(self, port, status):
        assert port == self.port
        status.value = 0
        return 0x77
    
    def spiGetAccumulatorAverage(self, port, status):
        assert port == self.port
        status.value = 0
        return 0x88
        
    def spiGetAccumulatorOutput(self, port, status):
        assert port == self.port
        status.value = 0
        return (0x99, 1)
        
def test_spi(wpilib):
    
    sim = SPISimulator()
    port = wpilib.SPI.Port.kMXP
    
    spi = wpilib.SPI(port, sim)
    assert sim.initialized == port
    
    spi.setChipSelectActiveHigh()
    assert sim.set_active_high == True
    
    spi.setChipSelectActiveLow()
    assert sim.set_active_low == True
    
    assert spi.transaction([1,2,3]) == [3,2,1]
    assert sim.tx == True
    
    assert spi.write([5,6,7]) == 3
    assert sim.wrote == True
    
    assert spi.read(False, 3) == [9, 9, 0]
    assert sim.did_read == True
    
    
    spi.freeAccumulator()
    assert sim.acc_freed == True
    
    spi.resetAccumulator()
    assert sim.acc_reset == True
    
    assert spi.getAccumulatorLastValue() == 0x55
    assert spi.getAccumulatorValue() == 0x66
    assert spi.getAccumulatorCount() == 0x77
    assert spi.getAccumulatorAverage() == 0x88
    assert spi.getAccumulatorOutput() == (0x99, 1)
    
    spi.free()
    assert sim.closed == True
    
    with pytest.raises(ValueError):
        spi.port
    
    