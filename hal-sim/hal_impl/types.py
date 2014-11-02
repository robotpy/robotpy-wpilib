#
# These are opaque types used internally by the simulation HAL
#

######################################################
# Semaphore
#############################################################################

# pthread opaque structures: TODO

class MUTEX_ID:
    pass

class SEMAPHORE_ID:
    pass

class MULTIWAIT_ID:
    pass


#############################################################################
# HAL
#############################################################################
    
class HALControlWord:
    def __init__(self):
        self.enabled = False
        self.autonomous = False
        self.test = False
        self.eStop = False
        self.fmsAttached = False
        self.dsAttached = False

class Port:
    def __init__(self, pin, module):
        self.pin = pin
        self.module = module

class HALJoystickAxes:
    def __init__(self):
        self.count = 0
        self.axes = 0 # TODO: C.c_int16 * kMaxJoystickAxes
_HALJoystickAxes = HALJoystickAxes
        
class HALJoystickPOVs:
    def __init__(self):
        self.count = 0
        self.povs = 0 # TODO: C.c_int16 * kMaxJoystickPOVs
_HALJoystickPOVs = HALJoystickPOVs
        
#############################################################################
# Analog
#############################################################################

# opaque analog port
class AnalogPort:
    pass

# opaque analog trigger
class AnalogTrigger:
    pass

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class PCM:
    pass


#############################################################################
# Digital
#############################################################################

# opaque digital port
class DigitalPort:
    pass

# opaque PWM
class PWM:
    pass

# opaque counter
class Counter:
    pass

# opaque encoder
class Encoder:
    pass

#############################################################################
# Interrupts
#############################################################################

# opaque interrupt
class Interrupt:
    pass

#############################################################################
# Notifier
#############################################################################

# opaque Notifier
class Notifier:
    pass

#############################################################################
# Solenoid
#############################################################################

# opaque SolenoidPort
class SolenoidPort:
    def __init__(self, port):
        self.pin = port.pin
        self.module = port.module


