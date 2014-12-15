import ctypes as C
from hal.constants import kMaxJoystickAxes, kMaxJoystickPOVs

__all__ = ["MUTEX_ID", "SEMAPHORE_ID", "MULTIWAIT_ID",
           "HALControlWord", "HALControlWord_ptr", "Port_ptr",
           "HALJoystickAxes", "HALJoystickAxes_ptr",
           "HALJoystickPOVs", "HALJoystickPOVs_ptr",
           "HALJoystickButtons", "HALJoystickButtons_ptr",
           "HALJoystickDescriptor", "HALJoystickDescriptor_ptr",
           "AnalogPort_ptr", "AnalogTrigger_ptr", "PCM_ptr", "DigitalPort_ptr", "PWM_ptr",
           "Counter_ptr", "Encoder_ptr", "Interrupt_ptr", "Notifier_ptr",
           "SolenoidPort", "SolenoidPort_ptr", "TalonSRX_ptr"]

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
HALControlWord_ptr = C.POINTER(HALControlWord)

# opaque port structure
class Port(C.Structure):
    pass
Port_ptr = C.POINTER(Port)

class HALJoystickAxes(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("axes", C.c_int16 * kMaxJoystickAxes)]
HALJoystickAxes_ptr = C.POINTER(HALJoystickAxes)

class HALJoystickPOVs(C.Structure):
    _fields_ = [("count", C.c_uint16),
                ("povs", C.c_int16 * kMaxJoystickPOVs)]
HALJoystickPOVs_ptr = C.POINTER(HALJoystickPOVs)

class HALJoystickButtons(C.Structure):
    _fields_ = [("buttons", C.c_uint32),
                ("count", C.c_uint8)]
HALJoystickButtons_ptr = C.POINTER(HALJoystickButtons)

class HALJoystickDescriptor(C.Structure):
    _fields_ = [("isXbox", C.c_uint8),
                ("type", C.c_uint8),
                ("name", C.c_char * 256),
                ("axisCount", C.c_uint8),
                ("axisTypes", C.c_uint8),
                ("buttonCount", C.c_uint8),
                ("povCount", C.c_uint8)]
HALJoystickDescriptor_ptr = C.POINTER(HALJoystickDescriptor)

#############################################################################
# Analog
#############################################################################

# opaque analog port
class AnalogPort(C.Structure):
    pass
AnalogPort_ptr = C.POINTER(AnalogPort)

# opaque analog trigger
class AnalogTrigger(C.Structure):
    pass
AnalogTrigger_ptr = C.POINTER(AnalogTrigger)

#############################################################################
# Compressor
#############################################################################

# opaque pcm
class PCM(C.Structure):
    pass
PCM_ptr = C.POINTER(PCM)


#############################################################################
# Digital
#############################################################################

# opaque digital port
class DigitalPort(C.Structure):
    pass
DigitalPort_ptr = C.POINTER(DigitalPort)

# opaque PWM
class PWM(C.Structure):
    pass
PWM_ptr = C.POINTER(PWM)

# opaque counter
class Counter(C.Structure):
    pass
Counter_ptr = C.POINTER(Counter)

# opaque encoder
class Encoder(C.Structure):
    pass
Encoder_ptr = C.POINTER(Encoder)

#############################################################################
# Interrupts
#############################################################################

# opaque interrupt
class Interrupt(C.Structure):
    pass
Interrupt_ptr = C.POINTER(Interrupt)

#############################################################################
# Notifier
#############################################################################

# opaque Notifier
class Notifier(C.Structure):
    pass
Notifier_ptr = C.POINTER(Notifier)

#############################################################################
# Solenoid
#############################################################################

# opaque SolenoidPort
class SolenoidPort(C.Structure):
    _fields_ = [('pin', C.c_uint8),
                ('module', C.c_uint8)]
SolenoidPort_ptr = C.POINTER(SolenoidPort)

#############################################################################
# TalonSRX
#############################################################################

# opaque TalonSRX
class TalonSRX(C.Structure):
    pass
TalonSRX_ptr = C.POINTER(TalonSRX)
