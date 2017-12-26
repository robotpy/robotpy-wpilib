
from . import data
hal_data = data.hal_data

class SPISimBase:
    '''
        Base class to use for SPI protocol simulators.
        
        Has all functions that need to be implemented, but throws exceptions
        when data is asked of it. Will throw away set* function data, as most
        low-fidelity simulation will probably not care about such things. 
    '''
    
    def initializeSPI(self, port, status):
        self.port = port
        status.value = 0
    
    def transactionSPI(self, port, dataToSend, dataReceived, size):
        '''
            To give data back use ``data_received``::
            
                data_received[:] = [1,2,3...]
            
            :returns: number of bytes returned
        '''
        raise NotImplementedError
    
    def writeSPI(self, port, dataToSend, sendSize):
        ''':returns: number of bytes written'''
        return sendSize
    
    def readSPI(self, port, buffer, count):
        '''
            To give data, do ``buffer[:] = [1,2,3...]``
            
            :returns: number of bytes read
        '''
        raise NotImplementedError
    
    def closeSPI(self, port):
        pass
    
    def setSPISpeed(self, port, speed):
        pass
    
    def setSPIOpts(self, port, msbFirst, sampleOnTrailing, clkIdleHigh):
        pass
    
    def setSPIChipSelectActiveHigh(self, port, status):
        pass
    
    def setSPIChipSelectActiveLow(self, port, status):
        pass
    
    def getSPIHandle(self, port):
        pass
    
    def setSPIHandle(self, port, handle):
        pass

    def initSPIAuto(self, port, bufferSize, status):
        status.value = 0

    def freeSPIAuto(self, port, status):
        status.value = 0

    def startSPIAutoRate(self, port, period, status):
        status.value = 0

    def startSPIAutoTrigger(self, port, digitalSourceHandle, analogTriggerType, triggerRising, triggerFalling, status):
        status.value = 0

    def stopSPIAuto(self, port, status):
        status.value = 0

    def setSPIAutoTransmitData(self, port, dataToSend, dataSize, zeroSize, status):
        status.value = 0

    def forceSPIAutoRead(self, port, status):
        status.value = 0

    def readSPIAutoReceivedData(self, port, buffer, numToRead, timeout, status):
        ''':returns: number of bytes read'''
        raise NotImplementedError

    def getSPIAutoDroppedCount(self, port, status):
        ''':returns: int32'''
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
    
    def initializeSPI(self, port, status):
        self.angle_key = 'adxrs450_spi_%d_angle' % port
        self.rate_key = 'adxrs450_spi_%d_rate' % port
        
        print(self.angle_key)
    
    def getSPIAccumulatorAverage(self, port, status):
        return 0
    
    def getSPIAccumulatorValue(self, port, status):
        return int(hal_data['robot'].get(self.angle_key, 0) / (self.kDegreePerSecondPerLSB * self.kSamplePeriod))
    
    def getSPIAccumulatorLastValue(self, port, status):
        return int(hal_data['robot'].get(self.rate_key, 0) / self.kDegreePerSecondPerLSB)
    
    # for calibrate
    def writeSPI(self, port, data_to_send, send_size):
        return send_size
    
    def readSPI(self, port, buffer, count):
        buffer[:] = (0xff000000 | (0x5200 << 5)).to_bytes(4, 'big')
        return count
