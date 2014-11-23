import ctypes as C
from hal.constants import kMaxJoystickAxes, kMaxJoystickPOVs

__all__ = ["MUTEX_ID", "SEMAPHORE_ID", "MULTIWAIT_ID",
           "HALControlWord", "HALControlWordPtr", "Port",
           "_HALJoystickAxes", "HALJoystickAxes",
           "_HALJoystickPOVs", "HALJoystickPOVs",
           "_HALJoystickButtons", "HALJoystickButtons",
           "AnalogPort", "AnalogTrigger", "PCM", "DigitalPort", "PWM",
           "Counter", "Encoder", "Interrupt", "Notifier",
           "_SolenoidPort", "SolenoidPort"]

#############################################################################
# Semaphore
#############################################################################


# pthread opaque structures
class _pthread_mutex_t(C.Structure):
    pass
MUTEX_ID = C.POINTER(_pthread_mutex_t)

class _sem_t(C.Structure):
    pass
SEMAPHORE_ID = C.POINTER(_sem_t)

class _pthread_cond_t(C.Structure):
    pass
MULTIWAIT_ID = C.POINTER(_pthread_cond_t)


#############################################################################
# HAL
#############################################################################

class HALControlWord(C.Structure):
    _fields_ = [("enabled", C.c_uint32, 1),
                ("autonomous", C.c_uint32, 1),
                ("test", C.c_uint32, 1),
                ("eStop", C.c_uint32, 1),
                ("fmsAttached", C.c_uint32, 1),
                ("dsAttached", C.c_uint32, 1),
                ("control_reserved", C.c_uint32, 26)]
HALControlWordPtr = C.POINTER(HALControlWord)

# opaque port structure
class _Port(C.Structure):
    pass
Port = C.POINTER(_Port)

class _HALJoystickAxes(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("axes", C.c_int16 * kMaxJoystickAxes)]
HALJoystickAxes = C.POINTER(_HALJoystickAxes)

class _HALJoystickPOVs(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("povs", C.c_int16 * kMaxJoystickPOVs)]
HALJoystickPOVs = C.POINTER(_HALJoystickPOVs)

class _HALJoystickButtons(C.Structure):
    _fields_ = [("buttons", C.c_uint32),
                ("count", C.c_uint8)]
HALJoystickButtons = C.POINTER(_HALJoystickButtons)

#############################################################################
# Analog
#############################################################################

# opaque analog port
class _AnalogPort(C.Structure):
    pass
AnalogPort = C.POINTER(_AnalogPort)

# opaque analog trigger
class _AnalogTrigger(C.Structure):
    pass
AnalogTrigger = C.POINTER(_AnalogTrigger)

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class _PCM(C.Structure):
    pass
PCM = C.POINTER(_PCM)


#############################################################################
# Digital
#############################################################################

# opaque digital port
class _DigitalPort(C.Structure):
    pass
DigitalPort = C.POINTER(_DigitalPort)

# opaque PWM
class _PWM(C.Structure):
    pass
PWM = C.POINTER(_PWM)

# opaque counter
class _Counter(C.Structure):
    pass
Counter = C.POINTER(_Counter)

# opaque encoder
class _Encoder(C.Structure):
    pass
Encoder = C.POINTER(_Encoder)

#############################################################################
# Interrupts
#############################################################################

# opaque interrupt
class _Interrupt(C.Structure):
    pass
Interrupt = C.POINTER(_Interrupt)

#############################################################################
# Notifier
#############################################################################

# opaque Notifier
class _Notifier(C.Structure):
    pass
Notifier = C.POINTER(_Notifier)

#############################################################################
# Solenoid
#############################################################################

# opaque SolenoidPort
class _SolenoidPort(C.Structure):
    _fields_ = [('pin', C.c_uint8),
                ('module', C.c_uint8)]
SolenoidPort = C.POINTER(_SolenoidPort)
