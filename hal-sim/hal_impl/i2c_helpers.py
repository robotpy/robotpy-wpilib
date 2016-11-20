
from . import data
hal_data = data.hal_data

class I2CSimBase:
    '''
        Base class to use for i2c protocol simulators.
        
        Not particularly useful at the moment
    '''
    
    def initializeI2C(self, port, status):
        self.port = port
        status.value = 0
    
    def transactionI2C(self, port, deviceAddress, dataToSend, sendSize, dataReceived, receiveSize):
        '''
            To give data back use ``data_received``::
            
                data_received[:] = [1,2,3...]
            
            :returns: number of bytes returned
        '''
        raise NotImplementedError
    
    def writeI2C(self, port, deviceAddress, dataToSend, sendSize):
        ''':returns: number of bytes written'''
        return sendSize
    
    def readI2C(self, port, deviceAddress, buffer, count):
        '''
            To give data, do ``buffer[:] = [1,2,3...]``
            
            :returns: number of bytes read
        '''
        raise NotImplementedError
    
    def closeI2C(self, port):
        pass
    
