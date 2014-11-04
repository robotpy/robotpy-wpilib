import ctypes as C

__all__ = ["_dll", "_RETFUNC", "_VAR"]

_dll = C.CDLL("./libHALAthena_shared.so", use_errno=True)

def _RETFUNC(name, restype, *params, out=None, library=_dll,
             errcheck=None, handle_missing=False):
    prototype = C.CFUNCTYPE(restype, *tuple(param[1] for param in params))
    paramflags = []
    for param in params:
        if out is not None and param[0] in out:
            dir = 2
        else:
            dir = 1
        if len(param) == 3:
            paramflags.append((dir, param[0], param[2]))
        else:
            paramflags.append((dir, param[0]))
    try:
        func = prototype((name, library), tuple(paramflags))
        if errcheck is not None:
            func.errcheck = errcheck
    except AttributeError:
        if not handle_missing:
            raise
        def func(*args, **kwargs):
            raise NotImplementedError
    return func

def _VAR(name, type, library=_dll):
    return type.in_dll(library, name)
