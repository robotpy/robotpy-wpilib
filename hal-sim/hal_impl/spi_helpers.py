
from . import data
hal_data = data.hal_data

class SPISimBase:
    '''
        Base class to use for SPI protocol simulators.
        
        Has all functions that need to be implemented, but throws exceptions
        when data is asked of it. Will throw away set* function data, as most
        low-fidelity simulation will probably not care about such things. 
    '''
    
    def spiInitialize(self, port, status):
        self.port = port
        status.value = 0
    
    def spiTransaction(self, port, data_to_send, data_received, size):
        '''
            To give data back use ``data_received``::
            
                data_received[:] = [1,2,3...]
            
            :returns: number of bytes returned
        '''
        raise NotImplementedError
    
    def spiWrite(self, port, data_to_send, send_size):
        ''':returns: number of bytes written'''
        return send_size
    
    def spiRead(self, port, buffer, count):
        '''
            To give data, do ``buffer[:] = [1,2,3...]``
            
            :returns: number of bytes read
        '''
        raise NotImplementedError
    
    def spiClose(self, port):
        pass
    
    def spiSetSpeed(self, port, speed):
        pass
    
    def spiSetOpts(self, port, msb_first, sample_on_trailing, clk_idle_high):
        pass
    
    def spiSetChipSelectActiveHigh(self, port, status):
        pass
    
    def spiSetChipSelectActiveLow(self, port, status):
        pass
    
    def spiGetHandle(self, port):
        pass
    
    def spiSetHandle(self, port, handle):
        pass
        
    def spiInitAccumulator(self, port,
                           period, cmd, xfer_size, valid_mask, valid_value,
                           data_shift, data_size, is_signed, big_endian, status):
        pass
        
    def spiFreeAccumulator(self, port, status):
        pass
        
    def spiResetAccumulator(self, port, status):
        pass
    
    def spiSetAccumulatorCenter(self, port, center, status):
        pass
        
    def spiSetAccumulatorDeadband(self, port, deadband, status):
        pass
        
    def spiGetAccumulatorLastValue(self, port, status):
        ''':returns: int32'''
        raise NotImplementedError
        
    def spiGetAccumulatorValue(self, port, status):
        ''':returns: int64'''
        raise NotImplementedError
        
    def spiGetAccumulatorCount(self, port, status):
        ''':returns: int32'''
        raise NotImplementedError
    
    def spiGetAccumulatorAverage(self, port, status):
        ''':returns: float'''
        raise NotImplementedError
        
    def spiGetAccumulatorOutput(self, port, status):
        ''':returns: value(int64), count(int32)'''
        raise NotImplementedError
        


class ADXRS450_Gyro_Sim(SPISimBase):
    '''
        This returns the angle of the gyro as the value of::
            
            hal_data['robot']['adxrs450_spi_%d_angle']
            
        Where %d is the i2c port number. Angle should be in degrees.
    '''
    
    def __init__(self, gyro):
        self.kDegreePerSecondPerLSB = gyro.kDegreePerSecondPerLSB
        self.kSamplePeriod = gyro.kSamplePeriod
    
    def spiInitialize(self, port, status):
        self.angle_key = 'adxrs450_spi_%d_angle' % port
        self.rate_key = 'adxrs450_spi_%d_rate' % port
        
        print(self.angle_key)
    
    def spiGetAccumulatorAverage(self, port, status):
        return 0
    
    def spiGetAccumulatorValue(self, port, status):
        return hal_data['robot'].get(self.angle_key, 0) / (self.kDegreePerSecondPerLSB * self.kSamplePeriod)
    
    def spiGetAccumulatorLastValue(self, port, status):
        return hal_data['robot'].get(self.rate_key, 0) / self.kDegreePerSecondPerLSB
    
    # for calibrate
    def spiWrite(self, port, data_to_send, send_size):
        return send_size
    
    def spiRead(self, port, buffer, count):
        buffer[:] = (0xff000000 | (0x5200 << 5)).to_bytes(4, 'big')
        return count
    