#
# These are opaque types used internally by the simulation HAL
#

import copy

__all__ = ["MUTEX_ID", "MULTIWAIT_ID",
           "HALControlWord_ptr", "HALControlWord",
           "Port_ptr", "Port",
           "HALJoystickAxes_ptr", "HALJoystickAxes",
           "HALJoystickPOVs_ptr", "HALJoystickPOVs",
           "HALJoystickButtons_ptr", "HALJoystickButtons",
           "HALJoystickDescriptor_ptr", "HALJoystickDescriptor",
           "AnalogPort_ptr", "AnalogPort",
           "AnalogTrigger_ptr", "AnalogTrigger",
           "PCM_ptr", "PCM",
           "DigitalPort_ptr", "DigitalPort",
           "PWM_ptr", "PCM",
           "Counter_ptr", "Counter",
           "Encoder_ptr", "Encoder",
           "Interrupt_ptr", "Interrupt",
           "Notifier_ptr", "Notifier",
           "SolenoidPort_ptr", "SolenoidPort",
           "TalonSRX_ptr", "TalonSRX"]

class _fakeptr(object):
    fake_pointer = True

#Fake pointer emulating a c.POINTER()
def fake_pointer(orig_obj, name=None):
    if name is None:
        name = orig_obj.__name__
    obj = type(name, (orig_obj, ), _fakeptr.__dict__.copy())
    return obj


#############################################################################
# Semaphore
#############################################################################

class _MUTEX_ID:
    def __init__(self, lock):
        self.lock = lock
MUTEX_ID = fake_pointer(_MUTEX_ID, "MUTEX_ID")

class _MULTIWAIT_ID:
    def __init__(self, cond):
        self.cond = cond
MULTIWAIT_ID = fake_pointer(_MULTIWAIT_ID, "MULTIWAIT_ID")

#############################################################################
# HAL
#
# Profiling note: it seems to be faster to use __slots__ and to not have
#                 constructors for things that are created often, and just
#                 set the attributes externally. Python 3.4, linux
#
#############################################################################

class HALControlWord:
    pass
HALControlWord_ptr = fake_pointer(HALControlWord)

class Port:
    __slots__ = ['pin', 'module']
    def __init__(self, pin, module):
        self.pin = pin
        self.module = module
Port_ptr = fake_pointer(Port)

class HALJoystickAxes:
    __slots__ = ['count', 'axes']
HALJoystickAxes_ptr = fake_pointer(HALJoystickAxes)

class HALJoystickPOVs:
    __slots__ = ['count', 'povs']
HALJoystickPOVs_ptr = fake_pointer(HALJoystickPOVs)

class HALJoystickButtons:
    __slots__ = ['buttons', 'count']
HALJoystickButtons_ptr = fake_pointer(HALJoystickButtons)

class HALJoystickDescriptor:
    __slots__ = ['isXbox', 'type', 'name', 'axisCount', 'buttonCount']
    def __init__(self, d={}):
        self.isXbox = d.get('isXbox', False)
        self.type = d.get('type', 0)
        self.name = d.get('name', '')
        self.axisCount = d.get("axisCount", 0)
        self.buttonCount = d.get("buttonCount", 0)
HALJoystickDescriptor_ptr = fake_pointer(HALJoystickDescriptor)

#############################################################################
# Analog
#############################################################################

# opaque analog port
class AnalogPort:
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin
AnalogPort_ptr = fake_pointer(AnalogPort)

# opaque analog trigger
class AnalogTrigger:
    __slots__ = ['pin', 'index']
    def __init__(self, port, index):
        self.pin = port.pin
        self.index = index
AnalogTrigger_ptr = fake_pointer(AnalogTrigger)

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class PCM:
    __slots__ = ['pcmid']
    def __init__(self, pcmid):
        self.pcmid = pcmid
PCM_ptr = fake_pointer(PCM)


#############################################################################
# Digital
#############################################################################

# opaque digital port
class DigitalPort:
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin
DigitalPort_ptr = fake_pointer(DigitalPort)

# opaque PWM
class PWM:
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx
PWM_ptr = fake_pointer(PWM)

# opaque counter
class Counter:
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx
Counter_ptr = fake_pointer(Counter)

# opaque encoder
class Encoder:
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx
Encoder_ptr = fake_pointer(Encoder)

#############################################################################
# Interrupts
#############################################################################

# opaque interrupt
class Interrupt:
    pass
Interrupt_ptr = fake_pointer(Interrupt)

#############################################################################
# Notifier
#############################################################################

# opaque Notifier
class Notifier:
    pass
Notifier_ptr = fake_pointer(Notifier)

#############################################################################
# Solenoid
#############################################################################

# opaque SolenoidPort
class SolenoidPort:
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin
SolenoidPort_ptr = fake_pointer(SolenoidPort)


#############################################################################
# TalonSRX
#############################################################################

# opaque TalonSRX
class TalonSRX:
    __slots__ = ['id']
    def __init__(self, deviceNumber):
        self.id = deviceNumber
TalonSRX_ptr = fake_pointer(TalonSRX)
