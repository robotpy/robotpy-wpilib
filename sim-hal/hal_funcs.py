
#
# This is the start of an alternative implementation around the hal implementation
#

import ctypes as C
import inspect

import hal_impl as _dll

def gen_check(pname, ptype):
    
    if ptype is C.c_bool:
        return 'isinstance(%s, bool)' % pname
    
    elif ptype in [C.c_float, C.c_double, C.c_longdouble]:
        return 'isinstance(%s, float)' % pname
    
    elif ptype is C.c_char:
        return 'isinstance(%s, bytes) and len(%s) == 1' % (pname, pname)
    elif ptype is C.c_wchar:
        return 'isinstance(%s, str) and len(%s) == 1' % (pname, pname)
    elif ptype is C.c_char_p:
        return '%s is None or isinstance(%s, bytes)' % (pname, pname)
    elif ptype is C.c_wchar_p:
        return '%s is None or isinstance(%s, bytes)' % (pname, pname)
    
    elif ptype in [C.c_int, C.c_long, C.c_longlong]:
        return 'isinstance(%s, int)' % pname
    elif ptype in [C.c_byte, C.c_int8]:
        return 'isinstance(%s, int) and %s < %d and %s > -%d' % (pname, pname, 1<<7, pname, 1<<7)
    elif ptype is C.c_int16:
        return 'isinstance(%s, int) and %s < %d and %s > -%d' % (pname, pname, 1<<15, pname, 1<<15)
    elif ptype is C.c_int32:
        return 'isinstance(%s, int) and %s < %d and %s > -%d' % (pname, pname, 1<<31, pname, 1<<31)
    elif ptype is C.c_int64:
        return 'isinstance(%s, int) and %s < %d and %s > -%d' % (pname, pname, 1<<63, pname, 1<<63)
        
    elif ptype in [C.c_uint, C.c_size_t]:
        return 'isinstance(%s, int)' % (pname, pname, pname)
    elif ptype is C.c_uint8:
        return 'isinstance(%s, int) and %s < %d and %s >= 0' % (pname, pname, 1<<8, pname)
    elif ptype is C.c_uint16:
        return 'isinstance(%s, int) and %s < %d and %s >= 0' % (pname, pname, 1<<16, pname)
    elif ptype is C.c_uint32:
        return 'isinstance(%s, int) and %s < %d and %s >= 0' % (pname, pname, 1<<32, pname)
    elif ptype is C.c_uint64:
        return 'isinstance(%s, int) and %s < %d and %s >= 0' % (pname, pname, 1<<64, pname)
    
    else:
        raise 'isinstance(%s, %s)' % (pname, ptype)
    

def gen_func(f, name, restype, params, out):
    
    args = []
    checks = []
    
    if out is None:
        out = []
    
    for pname, ptype in params:
        if pname not in out:
            
            check = gen_check(pname, ptype)
            checks.append('assert %s, "%s; with %s=%%s, type(%s)=%%s" %% (%s, type(%s).__name__)' % (check, check, pname, pname, pname, pname)) 
            
            args.append(pname)
    
    # double check that our simulated HAL is correct
    info = inspect.getfullargspec(f)
    assert info.args == args, '%s != %s' % (info.args, args)
    
    # Create the function body to be exec'ed
    return inspect.cleandoc('''
        def %s(%s):
            %s
            return _dll.%s(%s)
    ''') % (name, ', '.join(args), 
            '    '.join(checks),
            name, ', '.join(args))    


def _RETFUNC(name, restype, *params, out=None, library=_dll,
             errcheck=None, handle_missing=False):
    
    # get func
    try:
        fn = getattr(_dll, name)
    except:
        return  # TEMP remove this!
        
    fn_body = gen_func(fn, name, restype, params, out)
    #print(fn_body)
    
    # exec:
    # TODO: give it a filename?
    locals = {}
    exec(fn_body, locals)
    
    # return the created func
    return locals[name]


def _VAR(name, type, library=_dll):
    try:
        return getattr(_dll, name)
    except:
        pass    # TEMP, remove this