
from . import data
hal_data = data.hal_data

class I2CSimBase:
    '''
        Base class to use for i2c protocol simulators.
        
        Not particularly useful at the moment
    '''
    
    def i2CInitialize(self, port, status):
        self.port = port
        status.value = 0
    
    def i2CTransaction(self, port, device_address, data_to_send, send_size, data_received, receive_size):
        '''
            To give data back use ``data_received``::
            
                data_received[:] = [1,2,3...]
            
            :returns: number of bytes returned
        '''
        raise NotImplementedError
    
    def i2CWrite(self, port, device_address, data_to_send, send_size):
        ''':returns: number of bytes written'''
        return send_size
    
    def i2CRead(self, port,  device_address, buffer, count):
        '''
            To give data, do ``buffer[:] = [1,2,3...]``
            
            :returns: number of bytes read
        '''
        raise NotImplementedError
    
    def i2CClose(self, port):
        pass
    
