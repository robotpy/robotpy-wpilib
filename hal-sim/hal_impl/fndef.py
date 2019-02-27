#
# This is the start of an alternative implementation around the hal implementation
#

import collections
import ctypes as C
import inspect
import os

from . import functions as _dll

__all__ = ["_dll", "_RETFUNC", "_VAR", "sleep"]

sleep = _dll.sleep

FuncData = collections.namedtuple(
    "FuncData",
    [
        "name",  # internal name
        "c_name",  # c name (used for validation)
        "restype",  # return type
        "params",  # list of [(name, type), ..]
        "out",  # output parameters, same form as params
    ],
)

from hal.exceptions import HALError


class SimulationError(HALError):
    """If you get this error, an undefined simulation error occurred"""


def gen_check(pname, ptype):

    # TODO: This does checks on normal types, but if you pass a ctypes value
    #       in then this does not check those properly.

    if ptype is C.c_bool:
        return "isinstance(%s, bool)" % pname

    elif ptype in [C.c_float, C.c_double, C.c_longdouble]:
        return "isinstance(%s, (int, float))" % pname

    elif ptype is C.c_char:
        return "isinstance(%s, bytes) and len(%s) == 1" % (pname, pname)
    elif ptype is C.c_wchar:
        return "isinstance(%s, str) and len(%s) == 1" % (pname, pname)
    elif ptype is C.c_char_p:
        return (
            "%s is None or isinstance(%s, bytes) or getattr(%s, '_type_') is _C.c_char"
            % (pname, pname, pname)
        )
    elif ptype is C.c_wchar_p:
        return "%s is None or isinstance(%s, bytes)" % (pname, pname)

    elif ptype in [C.c_int, C.c_long, C.c_longlong]:
        return "isinstance(%s, int)" % pname
    elif ptype in [C.c_byte, C.c_int8]:
        return "isinstance(%s, int) and %s < %d and %s > -%d" % (
            pname,
            pname,
            1 << 7,
            pname,
            1 << 7,
        )
    elif ptype is C.c_int16:
        return "isinstance(%s, int) and %s < %d and %s > -%d" % (
            pname,
            pname,
            1 << 15,
            pname,
            1 << 15,
        )
    elif ptype is C.c_int32:
        return "isinstance(%s, int) and %s < %d and %s > -%d" % (
            pname,
            pname,
            1 << 31,
            pname,
            1 << 31,
        )
    elif ptype is C.c_int64:
        return "isinstance(%s, int) and %s < %d and %s > -%d" % (
            pname,
            pname,
            1 << 63,
            pname,
            1 << 63,
        )

    elif ptype in [C.c_uint, C.c_size_t]:
        return "isinstance(%s, int)" % (pname)
    elif ptype is C.c_uint8:
        return "isinstance(%s, int) and %s < %d and %s >= 0" % (
            pname,
            pname,
            1 << 8,
            pname,
        )
    elif ptype is C.c_uint16:
        return "isinstance(%s, int) and %s < %d and %s >= 0" % (
            pname,
            pname,
            1 << 16,
            pname,
        )
    elif ptype is C.c_uint32:
        return "isinstance(%s, int) and %s < %d and %s >= 0" % (
            pname,
            pname,
            1 << 32,
            pname,
        )
    elif ptype is C.c_uint64:
        return "isinstance(%s, int) and %s < %d and %s >= 0" % (
            pname,
            pname,
            1 << 64,
            pname,
        )

    elif ptype is None:
        return "%s is None" % pname

    else:
        # TODO: do validation here
        # return 'isinstance(%s, %s)' % (pname, type(ptype).__name__)
        return None


def gen_func(f, name, restype, params, out, _thunk):

    args = []
    callargs = []
    checks = []
    retchecks = []

    if out is None:
        out = []

    # not actually a check, unpacks the first arg
    if _thunk:
        checks.append("_dll, %s = %s" % (params[0][0], params[0][0]))
        init = ""
        fn_call = "_dll.%s" % name
    else:
        init = "_dll_%s = _dll.%s" % (name, name)
        fn_call = "_dll_%s" % name

    # Generate a check for each parameter
    for param in params:
        pname, ptype = param[:2]

        if pname not in out:
            check = gen_check(pname, ptype)

            if check is not None:
                # the check is an assert, but we provide a better error message
                # otherwise these things will be impossible to debug
                checks.append(
                    "assert %s, \"invalid parameter '%s' (check was: %s); with %s=%%s, type(%s)=%%s\" %% (%s, type(%s).__name__)"
                    % (check, pname, check, pname, pname, pname, pname)
                )

            if len(param) == 3:
                args.append("%s=%s" % (pname, param[2]))
            else:
                args.append(pname)

            callargs.append(pname)

    # double check that our simulated HAL is correct
    info = inspect.getfullargspec(f)
    assert info.args == callargs, "%s: %s != %s" % (name, info.args, args)

    # Check the return value, just to be extra pedantic
    if out:
        if restype is None:
            retvals = out[:]
        else:
            retvals = [restype] + out
    else:
        retvals = [restype]

    if len(retvals) == 1:
        check = gen_check("return_value", retvals[0])
        if check is not None:
            retchecks.append(
                'assert %s, "Internal Error: Invalid return value from %s (check was: %s); value=%%s, type=%%s" %% (return_value, type(return_value).__name__)'
                % (check, name, check)
            )
    else:
        retchecks.append(
            'assert isinstance(return_value, tuple), "Internal Error: Invalid return value from %s (expected tuple, got %%s)" %% (return_value,)'
            % name
        )

        for i, r in enumerate(retvals):

            check = gen_check("return_value[%s]" % i, r)
            if check is not None:
                retchecks.append(
                    'assert %s, "Internal Error: Invalid return value from %s (check was: %s); value=%%s, type=%%s" %% (return_value, type(return_value).__name__)'
                    % (check, name, check)
                )

    # Create the function body to be exec'ed
    # -> optimization: store the function first, instead of looking it up in _dll each time
    return (
        inspect.cleandoc(
            """
        %s
        def %s(%s):
            try:
                %s
                return_value = %s(%s)
                %s
            except (NotImplementedError, HALError):
                raise
            except Exception as e:
                raise SimulationError("unexpected exception calling '%s'") from e
            else:
                return return_value
    """
        )
        % (
            init,
            name,
            ", ".join(args),
            "\n        ".join(checks),
            fn_call,
            ", ".join(args),
            "\n        ".join(retchecks),
            name,
        )
    )


def _RETFUNC(
    name,
    restype,
    *params,
    out=None,
    library=_dll,
    errcheck=None,
    handle_missing=False,
    _thunk=False,
    c_name=None
):

    # get func
    try:
        fn = getattr(_dll, name)
    except AttributeError:
        # only for use in the scanner
        if os.environ.get("HAL_NOSTRICT"):
            return
        raise

    try:
        fn_body = gen_func(fn, name, restype, params, out, _thunk)
    except AssertionError:
        if os.environ.get("HAL_NOSTRICT"):
            return
        raise

    # exec:
    # TODO: give it a filename?
    elocals = {"_C": C, "HALError": HALError, "SimulationError": SimulationError}
    if not _thunk:
        elocals["_dll"] = _dll

    exec(fn_body, elocals)

    # return the created func
    retfunc = elocals[name]

    if c_name is None:
        c_name = "HAL_%s%s" % (name[0].upper(), name[1:])

    # Store function definition data for API validation
    retfunc.fndata = FuncData(name, c_name, restype, params, out)
    return retfunc


def _THUNKFUNC(*a, **k):
    """This is the same as _RETFUNC, except that in simulation mode you should
       call _THUNKFUNC defined functions with a tuple of (simPort, param),
       allowing the API to implement objects where there are none
       
       The simPort object will be called with the normal function signature of
       the API call.
    """
    return _RETFUNC(_thunk=True, *a, **k)


def _VAR(name, type, library=_dll):
    """These are always constants, so it's ok to return a value"""
    return getattr(_dll, name)
