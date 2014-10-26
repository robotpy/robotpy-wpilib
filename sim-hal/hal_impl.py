
#
# TODO: organize imports... I think this needs the structs that are in hal, but
# hal needs the funcs in here... 
#

# TODO: actually implement this


# TODO: define the structure of this thing
hal_data = {
}


def _reset_hal_data():
    '''Intended to be used by the test runner'''
    global hal_data
    hal_data = {
    }

#############################################################################
# Semaphore
#############################################################################

def initializeMutexRecursive():
    pass

#############################################################################
# HAL
#############################################################################

def getPort(pin):
    pass

#############################################################################
# Accelerometer
#############################################################################

def setAccelerometerActive(active):
    pass

def setAccelerometerRange(range):
    pass

def getAccelerometerX():
    pass

def getAccelerometerY():
    pass

def getAccelerometerZ():
    pass

#############################################################################
# Analog
#############################################################################

# TODO


#############################################################################
# Compressor
#############################################################################

def initializeCompressor(module):
    pass

def checkCompressorModule(module):
    pass


#############################################################################
# Digital
#############################################################################

# TODO




# TODO TODO TODO... 

