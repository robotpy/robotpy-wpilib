#
# These are opaque types used internally by the simulation HAL
#

__all__ = [
    "ControlWord", "ControlWord_ptr",
    "JoystickAxes", "JoystickAxes_ptr",
    "JoystickPOVs", "JoystickPOVs_ptr",
    "JoystickButtons", "JoystickButtons_ptr",
    "JoystickDescriptor", "JoystickDescriptor_ptr",
    
    "Handle",
    "PortHandle",
    
    "AnalogInputHandle",
    "AnalogOutputHandle",
    "AnalogTriggerHandle",
    "CompressorHandle",
    "CounterHandle",
    "DigitalHandle",
    "DigitalPWMHandle",
    "EncoderHandle",
    "FPGAEncoderHandle",
    "GyroHandle",
    "InterruptHandle",
    "NotifierHandle",
    "RelayHandle",
    "SolenoidHandle",
]

class _fakeptr(object):
    fake_pointer = True

#Fake pointer emulating a c.POINTER()
def fake_pointer(orig_obj, name=None):
    if name is None:
        name = orig_obj.__name__
    obj = type(name, (orig_obj, ), _fakeptr.__dict__.copy())
    return obj


#############################################################################
# HAL
#
# Profiling note: it seems to be faster to use __slots__ and to not have
#                 constructors for things that are created often, and just
#                 set the attributes externally. Python 3.4, linux
#
#############################################################################

class ControlWord:
    pass
ControlWord_ptr = fake_pointer(ControlWord)

class JoystickAxes:
    __slots__ = ['count', 'axes']
JoystickAxes_ptr = fake_pointer(JoystickAxes)

class JoystickPOVs:
    __slots__ = ['count', 'povs']
JoystickPOVs_ptr = fake_pointer(JoystickPOVs)

class JoystickButtons:
    __slots__ = ['buttons', 'count']
JoystickButtons_ptr = fake_pointer(JoystickButtons)

class JoystickDescriptor:
    __slots__ = ['isXbox', 'type', 'name', 'axisCount', 'buttonCount']
    def __init__(self, d={}):
        self.isXbox = d.get('isXbox', False)
        self.type = d.get('type', 0)
        self.name = d.get('name', '')
        self.axisCount = d.get("axisCount", 0)
        self.buttonCount = d.get("buttonCount", 0)
JoystickDescriptor_ptr = fake_pointer(JoystickDescriptor)

#############################################################################
# Opaque handles
#############################################################################

class Handle:
    __slots__ = ()

class PortHandle(Handle):
    __slots__ = ['pin', 'module']
    def __init__(self, pin, module):
        self.pin = pin
        self.module = module

class AnalogInputHandle(Handle):
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin

class AnalogOutputHandle(Handle):
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin

class AnalogTriggerHandle(Handle):
    __slots__ = ['pin', 'index']
    def __init__(self, port, index):
        self.pin = port.pin
        self.index = index

class CompressorHandle(Handle):
    __slots__ = ['module']
    def __init__(self, module):
        self.module = module

class CounterHandle(Handle):
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx

class DigitalHandle:
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin

class DigitalPWMHandle(Handle):
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx

class EncoderHandle(Handle):
    __slots__ = ['idx']
    def __init__(self, idx):
        self.idx = idx

class FPGAEncoderHandle(Handle):
    pass

class GyroHandle(Handle):
    pass
    #def __init__(self, analoginput):
    #    self.analoginput = analoginput

class InterruptHandle(Handle):
    pass

class NotifierHandle(Handle):
    pass

class RelayHandle(Handle):
    pass

class SolenoidHandle(Handle):
    __slots__ = ['pin']
    def __init__(self, port):
        self.pin = port.pin

