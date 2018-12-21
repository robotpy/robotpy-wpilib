import argparse
import collections
import inspect
import os
from os.path import dirname, exists, join
import subprocess
import sys

import CppHeaderParser

green_head = "\033[92m"
red_head = "\033[91m"
orange_head = "\033[93m"
end_head = "\033[0m"
dash_bar = "-----------------------"
equals_bar = "======================="
class_start = dash_bar + "{}" + dash_bar
class_end = dash_bar + "End Class {}" + dash_bar
tab = "    "
arrowtab = "--> "


def get_hal_dirs(hal_dir):
    paths = list()
    paths.append(join(hal_dir, "hal"))
    return paths


# C/Normalized -> py
# key: c name, value: ctypes name, is_pointer
_ctypes_table = {
    "void": "None",
    "double": "C.c_double",
    "float": "C.c_float",
    "char": "C.c_char",
    "int8": "C.c_int8",
    "uint8": "C.c_uint8",
    "int16": "C.c_int16",
    "uint16": "C.c_uint16",
    "int32": "C.c_int32",
    "uint32": "C.c_uint32",
    "int64": "C.c_int64",
    "uint64": "C.c_uint64",
    "bool": "C.c_bool",
    "int": "C.c_int",
}

#
# Py/C -> normalized/C
# - The first item of each array is the normalized form of the type name
#


_normalize_type_aliases = [
    # fmt: off
   ["int32", "int", "i", "int32_t", "c_int", 'CTR_Code'],
   ["double", "d", "c_double"],
   ["float", "f", "c_float"],
   ["char", "z", "c"],
   ["void", "P"],
   ["int8", "int8_t", "c_int8", "b"],
   ["uint8", "uint8_t", "c_uint8", "B"],
   ["int16", "int16_t", "c_int16", "h", "c_short", "c_short_t", "short"],
   ["uint16", "uint16_t", "c_uint16", "H", "c_ushort", "c_ushort_t", "unsigned short"],
   ["uint32", "uint", "u", "c_uint", "I", "uint32_t"],
   ["uint64", "uint64_t", "c_uint64", "int64", "int64_t", "c_int64", "long", "l", "L", "longlong", "c_long", "long_t"],
   ["bool", "?", "HAL_Bool"]
    # fmt: on
]


def _process_header(fname):
    ppname = fname + ".pp"

    # Cannot cache result as we would need to check all dependencies too
    # fname_mtime = getmtime(fname)
    # ppname_mtime = 0
    # if exists(ppname):
    #     ppname_mtime = getmtime(ppname)

    print("Preprocessing " + fname, file=sys.stderr)

    args = [
        sys.executable,
        "-c",
        "import pcpp; pcpp.main()",
        "--passthru-unfound-includes",
        "-I",
        dirname(dirname(fname)),
        fname,
        "-o",
        ppname,
    ]
    subprocess.check_call(args)

    return CppHeaderParser.CppHeader(ppname)


def _normalize_type(obj):
    """
    Find the standard term for obj
    :param obj: A string name of a c type
    :returns The standard term for obj
    """

    for alias in _normalize_type_aliases:
        if obj in alias:
            return alias[0]
    return obj


def _py_to_normal(py_param):
    """
        Convert a python type to a normalized name, and indicate whether
        it is a pointer
    
        :returns: name, is_pointer
    """

    # TODO: function pointers are weird
    # if py_type_name == 'PyCFuncPtrType':
    #    if 'function' in c_type_name.lower():
    #        continue

    # Check py param pointer
    py_cls_name = py_param.__class__.__name__
    if py_cls_name == "PyCPointerType":
        py_pointer = True
        py_type_obj = py_param._type_
    elif py_cls_name == "PyCFuncPtrType":
        # CppHeaderParser doesn't parse function pointer typedefs correctly...
        # py_pointer = True
        # py_type_obj = py_param

        return "HAL_" + getattr(py_param, "_typedef_", "_FNPTR_NEEDS_typedef_"), False

    elif hasattr(py_param, "fake_pointer"):
        py_pointer = True
        py_type_obj = py_param
    else:
        py_pointer = False
        py_type_obj = py_param

    if hasattr(py_type_obj, "_type_"):
        # deal with char*
        if py_type_obj._type_ in ["z", "P"]:
            py_pointer = True
        py_type_name = _normalize_type(py_type_obj._type_)
    else:
        py_type_name = type(py_type_obj).__name__
        if py_type_name == "type":
            py_type_name = py_type_obj.__name__

        # All public types are prefixed with HAL_...
        py_type_name = "HAL_" + py_type_name

    return py_type_name, py_pointer


def _fn_name_to_py(n):
    # returns name, c_name
    if n.startswith("HAL_"):
        return n[4].lower() + n[5:], None
    else:
        return n, n


# enums.. key: name, value: type
_special_c_types = {}


class Type:
    """
        Stores normalized type information
        
        "normalized" is the form used in C decl
    """

    @classmethod
    def from_c(cls, typename, is_ptr):
        if typename.startswith("::"):
            typename = typename[2:]

        special_type = _special_c_types.get(typename)
        if special_type:
            typename = special_type.__name__
        typename = _normalize_type(typename)
        return cls(typename, is_ptr)

    @classmethod
    def from_py(cls, t):
        if t is None:
            return cls("void", False)
        else:
            name, is_ptr = _py_to_normal(t)
            return cls(name, is_ptr)

    def __init__(self, name, is_ptr):
        self.name = name
        self.is_ptr = is_ptr

    @property
    def repr_c(self):
        if self.is_ptr:
            return "%s*" % self.name
        else:
            return self.name

    @property
    def repr_py(self):
        name = self.name
        if name.startswith("HAL_"):
            name = name[4:]

        typ = _ctypes_table.get(name, name)
        if self.is_ptr:
            return "C.POINTER(%s)" % typ
        else:
            return typ


class Parameter:
    @classmethod
    def from_c(cls, p):
        is_ptr = True if p["pointer"] else False

        typ = p.get("raw_type")
        if not typ:
            typ = p["type"]

        return cls(p["name"], Type.from_c(typ, is_ptr))

    @classmethod
    def from_py(cls, name, typ):
        return cls(name, Type.from_py(typ))

    def __init__(self, name, typ):
        self.name = name
        self.type = typ

    @property
    def repr_c(self):
        return "%s %s" % (self.type.repr_c, self.name)

    @property
    def repr_py(self):
        return self.name


class Function:
    @classmethod
    def from_c(cls, fn):

        name = fn["name"]

        # Elide single void parameters
        if len(fn["parameters"]) == 1 and fn["parameters"][0]["raw_type"] == "void":
            params = []
        else:
            params = [Parameter.from_c(p) for p in fn["parameters"]]

        returns = Type.from_c(fn["returns"], True if fn["returns_pointer"] else False)

        return cls(fn, name, params, returns)

    @classmethod
    def from_py(cls, fn_name, fn):

        # Where does this belong?
        # if name != fn.name:
        #    raise ValueError("Error: for fn %s, name does match c_name %s" % (name, fn.name))

        #         args, varargs, keywords, _ = inspect.getargspec(obj)
        #         print(args, varargs)
        #         if varargs is not None:
        #             raise ValueError("HAL functions must not have varargs (%s)" % (fndata,))
        #
        #         if keywords is not None:
        #             raise ValueError("HAL functions must not have keywords (%s)" % (fndata,))
        #
        #         self.args = args

        fndata = fn.fndata
        name = fndata.c_name

        params = [Parameter.from_py(p[0], p[1]) for p in fndata.params]
        returns = Type.from_py(fndata.restype)

        return cls(fn, name, params, returns)

    def __init__(self, raw, name, params, returns):
        self.raw = raw

        self.name = name
        self.params = params
        self.returns = returns

        self.processed = False

    @property
    def repr_c(self):
        return "%s %s(%s)" % (
            self.returns.repr_c,
            self.name,
            ", ".join(p.repr_c for p in self.params),
        )

    @property
    def repr_py(self):
        return "%s(%s)" % (self.name, ", ".join(p.repr_py for p in self.params))

    @property
    def repr_pyhal(self):
        """
            Outputs RobotPy HAL ctypes declarations
        """

        name, c_name = _fn_name_to_py(self.name)

        functype = "_RETFUNC"
        params = self.params[:]

        if params and params[-1].name == "status":
            functype = "_STATUSFUNC"
            params.pop()

        text = name + " = " + functype + '("' + name + '", '

        text += self.returns.repr_py

        ptrs = []

        for param in params:
            text += ', ("' + param.name + '", ' + param.type.repr_py + ")"

            if param.type.is_ptr:
                ptrs.append(param.name)

        if len(ptrs):
            text += ', out=["' + '", "'.join(ptrs) + '"]'

        if c_name:
            text += ', c_name="%s"' % c_name

        text += ")"

        return text

    @property
    def repr_halsim(self):
        """
            Outputs RobotPy HAL simulation stubs
        """
        name, _ = _fn_name_to_py(self.name)

        text = "def %s(%s):" % (name, ", ".join(p.repr_py for p in self.params))

        if self.params and self.params[-1].name == "status":
            text += "\n    status.value = 0"

        text += "\n    raise NotImplementedError"
        text += "\n"

        return text

    def __repr__(self):
        return "<Function name=%s>" % self.name


class Class:
    @classmethod
    def from_c(cls, c_object):

        self = cls(c_object["name"])

        # collect subclasses
        for c in c_object["nested_classes"]:
            self.add_class(Class.from_c(c))

        for meth in c_object["methods"]["public"]:
            self.add_function(Function.from_c(meth))

        return self

    @classmethod
    def from_py(cls, py_name, py_obj, do_inspect=True):

        self = cls(py_name)

        if do_inspect:
            for name, o in inspect.getmembers(py_obj):
                if inspect.isclass(o):
                    self.add_class(Class.from_py(name, o, do_inspect=False))

                # TODO: inspect class methods
                elif hasattr(o, "fndata"):
                    self.add_function(Function.from_py(name, o))

                elif o is NotImplemented:
                    self.add_not_implemented_function(name)

        return self

    def __init__(self, name):
        self.name = name
        self.functions = collections.OrderedDict()
        self.classes = collections.OrderedDict()

    def add_class(self, c):
        existing = self.classes.setdefault(c.name, c)
        if existing is not c:
            raise ValueError("Duplicate class definitions found for %s" % c)

    def add_function(self, fn):
        existing = self.functions.setdefault(fn.name, fn)
        if existing is not fn:
            raise ValueError("Duplicate function definitions found for %s" % fn)

    def add_not_implemented_function(self, name):
        existing = self.functions.setdefault(
            "HAL_" + name[0].upper() + name[1:], NotImplemented
        )
        if existing is not NotImplemented:
            raise ValueError("Duplicate function definitions found for %s" % name)


class CHeader:
    def __init__(self, fname, header):

        self.functions = collections.OrderedDict()
        self.classes = collections.OrderedDict()

        self.fname = fname

        for fn in header.functions:
            cfn = Function.from_c(fn)
            item = self.functions.setdefault(cfn.name, cfn)
            if cfn is not item:
                print("Warning: ignored duplicate function: %s; %s" % (cfn, item))

        for cls in header.classes.values():
            ccls = Class.from_c(cls)
            item = self.classes.setdefault(ccls.name, ccls)
            if ccls is not item:
                raise ValueError("Duplicate class: %s; %s" % (ccls, item))


def collect_headers(header_dirs, filter_h=None):
    """
        Collects relevant header information in a normalized way to
        reduce compare logic later
    """

    headers = []

    # Get all header files in header_dirs
    for header_dir in header_dirs:
        for root, _, files in os.walk(header_dir):
            for fname in files:
                # Skip HAL.h - it simply includes all the other headers
                if fname == "HAL.h":
                    continue

                # Make sure it is a .hpp file
                if os.path.splitext(fname)[1] not in [".hpp", ".h"]:
                    continue

                fname = os.path.join(root, fname)

                # Gather the headers first, so we can populate the type list
                header = _process_header(fname)
                for enum in header.enums:
                    _special_c_types[enum["name"]] = enum["type"]

                # Process all the headers -- but only add them if they're in the
                # filtered set
                if not filter_h or fname.endswith(filter_h):
                    headers.append((fname, header))

            # Don't recurse
            break

    # Now actually process the headers
    headers = [CHeader(fname, header) for fname, header in headers]

    # Sort by filename
    headers.sort(key=lambda h: h.fname)

    return headers


class OutputItem:
    def __init__(self, fname, c, py):

        self.fname = fname

        self.c_item = c
        self.py_item = py

        self.ignored_errors = []
        self.errors = []
        self.warnings = []

    def compare(self, msg, c, py, warning=False):
        if c != py:
            if warning:
                self.add_warning("%s (c: %s, py: %s)", msg, c, py)
            else:
                self.add_error("%s (c: %s, py: %s)", msg, c, py)

    def add_error(self, msg, *args):
        self.errors.append(msg % args)

    def add_warning(self, msg, *args):
        self.warnings.append(msg % args)


def compare(headers, py_obj, match_py):

    outputs = []

    # for each c thing, ensure that it is in py and that it matches
    for header in headers:
        for c_fn in header.functions.values():
            py_fn = py_obj.functions.get(c_fn.name)
            output = OutputItem(header.fname, c_fn, py_fn)

            if py_fn is None:
                output.add_warning("py function does not exist")
            elif py_fn is not NotImplemented:
                py_fn.processed = True
                compare_fn(c_fn, py_fn, output)

            outputs.append(output)

    if match_py:
        # for each py thing, ensure that it is in C
        for py_fn in py_obj.functions.values():
            if py_fn is NotImplemented or py_fn.processed:
                continue

            output = OutputItem("Unmatched python functions", None, py_fn)
            output.add_error("C method does not exist")
            outputs.append(output)

    # count the number of errors and warnings
    num_errors = 0
    num_ignored_errors = 0
    num_warnings = 0

    for o in outputs:
        num_errors += len(o.errors)
        num_ignored_errors += len(o.ignored_errors)
        num_warnings += len(o.warnings)

    return outputs, num_errors, num_ignored_errors, num_warnings


def compare_fn(c_fn, py_fn, output):

    # Check the name
    output.compare("function name", c_fn.name, py_fn.name)

    # Check return type
    output.compare("return is pointer", c_fn.returns.is_ptr, py_fn.returns.is_ptr)

    output.compare("return type", c_fn.returns.name, py_fn.returns.name)

    # Do the arguments match?
    c_params = c_fn.params
    py_params = py_fn.params

    output.compare("number of arguments", len(c_params), len(py_params))

    for i, (c_param, py_param) in enumerate(zip(c_params, py_params)):

        output.compare(
            "parameter %s name" % i, c_param.name, py_param.name, warning=True
        )

        output.compare(
            "parameter %s (%s) is_ptr" % (i, c_param.name),
            c_param.type.is_ptr,
            py_param.type.is_ptr,
        )

        output.compare(
            "parameter %s (%s) type" % (i, c_param.name),
            c_param.type.name,
            py_param.type.name,
        )


def print_outputs(outputs, stubs=None, errors_only=False):

    last_fname = None

    for output in outputs:
        if output.fname != last_fname:
            print()
            print(output.fname)
            last_fname = output.fname

        start = green_head
        end = end_head

        if output.errors:
            start = red_head
        elif output.warnings:
            start = orange_head

        if output.c_item:
            print(start + output.c_item.repr_c + end)
        else:
            print(start + output.py_item.repr_py + end)

        for i in output.errors:
            print(start + "- ERR: " + i + end)

        if not errors_only:
            for i in output.warnings:
                print(start + "- " + i + end)

        if output.c_item and start != green_head:
            if stubs == "pyhal":
                print(output.c_item.repr_pyhal)
            elif stubs == "halsim":
                print(output.c_item.repr_halsim)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("hal_dir")
    # parser.add_argument('check_type', type=str, choices=['all', 'c', 'py'])
    parser.add_argument(
        "filter", type=str, default=None, nargs="?", help="Only process this filename"
    )

    parser.add_argument("--nostrict", action="store_true", default=False)
    parser.add_argument(
        "--stubs",
        type=str,
        choices=["no", "pyhal", "halsim"],
        default="no",
        help="Use pyhal/halsim to generate stubs",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress 'good' output and only show errors/warnings",
    )

    args = parser.parse_args()

    if args.nostrict:
        os.environ["HAL_NOSTRICT"] = "1"

    # Guarantee that this is being ran on the current source tree
    sys.path.insert(0, join(dirname(__file__), "..", "..", "..", "hal-base"))
    try:
        import hal
    except AttributeError:
        print("Note: you may want to specify --nostrict to avoid seeing this error")
        print()
        raise

    c_data = collect_headers(get_hal_dirs(args.hal_dir), args.filter)

    hal_data = Class.from_py("hal", hal)

    outputs, num_errors, num_ignored_errors, num_warnings = compare(
        c_data, hal_data, False if args.filter else True
    )

    if args.quiet:
        outputs = [o for o in outputs if o.errors or o.warnings]

    print_outputs(outputs, args.stubs)

    # Print error counts at the end, so we don't have to move the terminal
    print()
    print(
        "%s errors, %s ignored errors, %s warnings"
        % (num_errors, num_ignored_errors, num_warnings)
    )
    print()

    if num_errors:
        return 1
    else:
        return 0


if __name__ == "__main__":
    exit(main())
