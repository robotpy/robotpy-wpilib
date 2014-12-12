#
# These are opaque types used internally by the simulation HAL
#

import copy

__all__ = ["MUTEX_ID", "SEMAPHORE_ID", "MULTIWAIT_ID",
           "HALControlWord", "HALControlWordPtr", "Port",
           "_HALJoystickAxes", "HALJoystickAxes",
           "_HALJoystickPOVs", "HALJoystickPOVs",
           "_HALJoystickButtons", "HALJoystickButtons",
           "_HALJoystickDescriptor", "HALJoystickDescriptor",
           "AnalogPort", "AnalogTrigger", "PCM", "DigitalPort", "PWM",
           "Counter", "Encoder", "Interrupt", "Notifier",
           "_SolenoidPort", "SolenoidPort", "TalonSRX"]

#############################################################################
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
    def __init__(self, d={}):
        self.enabled = d.get('enabled', False)
        self.autonomous = d.get('autonomous', False)
        self.test = d.get('test', False)
        self.eStop = d.get('eStop', False)
        self.fmsAttached = d.get('fms_attached',False)
        self.dsAttached = d.get('ds_attached', False)
HALControlWordPtr = HALControlWord

class Port:
    def __init__(self, pin, module):
        self.pin = pin
        self.module = module

class HALJoystickAxes:
    def __init__(self, axes=[]):
        self.count = len(axes)
        self.axes = axes[:]
_HALJoystickAxes = HALJoystickAxes

class HALJoystickPOVs:
    def __init__(self, povs=[]):
        self.count = len(povs)
        self.povs = povs
_HALJoystickPOVs = HALJoystickPOVs

class HALJoystickButtons:
    def __init__(self, buttons=0, count=0):
        self.buttons = buttons
        self.count = count
_HALJoystickButtons = HALJoystickButtons

class HALJoystickDescriptor:
    def __init__(self, d={}):
        self.isXbox = d.get('isXbox', False)
        self.type = d.get('type', 0)
        self.name = d.get('name', '')
        self.axisCount = d.get("axisCount", 0)
        self.buttonCount = d.get("buttonCount", 0)
_HALJoystickDescriptor = HALJoystickDescriptor

#############################################################################
# Analog
#############################################################################

# opaque analog port
class AnalogPort:
    def __init__(self, port):
        self.pin = port.pin

# opaque analog trigger
class AnalogTrigger:
    def __init__(self, port):
        self.pin = port.pin

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
    def __init__(self, idx):
        self.idx = idx

# opaque counter
class Counter:
    def __init__(self, idx):
        self.idx = idx

# opaque encoder
class Encoder:
    def __init__(self, idx):
        self.idx = idx

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
_SolenoidPort = SolenoidPort

#############################################################################
# TalonSRX
#############################################################################

# opaque TalonSRX
class TalonSRX:
    pass
