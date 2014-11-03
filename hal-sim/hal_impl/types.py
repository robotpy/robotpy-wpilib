#
# These are opaque types used internally by the simulation HAL
#

import copy

######################################################
# Semaphore
#############################################################################

class MUTEX_ID:
    def __init__(self, lock):
        self.lock = lock

class SEMAPHORE_ID:
    def __init__(self, sem):
        self.sem = sem

class MULTIWAIT_ID:
    def __init__(self, cond):
        self.cond = cond


#############################################################################
# HAL
#############################################################################

class HALControlWord:
    def __init__(self, d):
        self.enabled = d['enabled']
        self.autonomous = d['autonomous']
        self.test = d['test']
        self.eStop = d['eStop']
        self.fmsAttached = d['fms_attached']
        self.dsAttached = d['ds_attached']

class Port:
    def __init__(self, pin, module):
        self.pin = pin
        self.module = module

class HALJoystickAxes:
    def __init__(self, axes):
        self.count = len(axes)
        self.axes = axes[:]
_HALJoystickAxes = HALJoystickAxes

class HALJoystickPOVs:
    def __init__(self, povs):
        self.count = len(povs)
        self.povs = povs
_HALJoystickPOVs = HALJoystickPOVs

#############################################################################
# Analog
#############################################################################

# opaque analog port
class AnalogPort:
    def __init__(self, port):
        self.pin = port.pin

# opaque analog trigger
class AnalogTrigger:
    pass

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class PCM:
    def __init__(self, pcmid):
        self.pcmid = pcmid 


#############################################################################
# Digital
#############################################################################

# opaque digital port
class DigitalPort:
    def __init__(self, port):
        self.pin = port.pin

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


