import os
from os.path import dirname, join
import sys
import CppHeaderParser
import inspect

import argparse

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
    paths.append(join(hal_dir, 'include', 'HAL'))
    return paths

def index_py_funcs(python_objects):
    '''
        Collect python functions and create an index to them by c_name
    '''
    return [(pymod, index_py_obj(pymod)) for pymod in python_objects]
        
def index_py_obj(py_obj):
    functions = {}
    classes = {}
    
    for name, obj in inspect.getmembers(py_obj):
        if inspect.isclass(obj):
            classes[name] = obj
        else:
            fndata = getattr(obj, 'fndata', None)
            if fndata is not None:
                # check for conflicts
                existing = functions.get(fndata.c_name)
                if existing is not None:
                    raise ValueError("Error: name %s is used twice (%s; %s)" % (fndata, existing))
                
                functions[fndata.c_name] = (obj, fndata)
        
    return {'functions': functions, 'classes': classes}
    

def compare_header_dirs(python_objects, header_dirs, filter_h=None):
    """
    Parses through cpp_dirs and matches c++ header objects to front-end objects in
    python_object and returns a summary of it's findings.
    """

    output = dict()
    output["errors"] = 0
    output["ignored_errors"] = 0
    output["methods"] = list()
    output["classes"] = list()

    #Get the .. not_implemented ignore flags in the docstring of python_object
    children_to_ignore = []
    for python_object, _ in python_objects:
        children_to_ignore += parse_docstring(python_object.__doc__)

    #Get all header files in header_dirs
    for header_dir in header_dirs:
        for root, _, files in os.walk(header_dir):
            for fname in files:
                if filter_h and fname != filter_h:
                    continue
                _process_header(os.path.join(root, fname), output, children_to_ignore, python_objects)
    
    return output

def _process_header(header_file, output, children_to_ignore, python_objects):

    #Make sure it is a .hpp file
    if os.path.splitext(header_file)[1] not in [".hpp", ".h"]:
        return
    
    #For each class declaration
    header = CppHeaderParser.CppHeader(header_file)
    filename = os.path.basename(header_file)

    #Scan classes
    for c_class_name in header.classes:
        c_class = header.classes[c_class_name]
        #Do we ignore?
        ignore_child = c_class["name"] in children_to_ignore

        #Get the first python object and compare!
        python_child = None
        for _, idx in python_objects:
            python_child = idx['classes'].get(c_class["name"])
            if python_child is not None:
                break

        class_output = compare_class(python_child, c_class, filename)

        #Collect errors
        output["ignored_errors"] += class_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += class_output["errors"]
            class_output["ignored"] = True
        else:
            output["errors"] += len(class_output["errors"])
        output["classes"].append(class_output)

    #Scan methods
    for c_method in header.functions:
        #Do we ignore?
        ignore_child = c_method["name"] in children_to_ignore

        #Get the first python object and compare!
        python_child = None
        fndata = None
        c_name = c_method["name"]
        for _, idx in python_objects:
            python_child = idx['functions'].get(c_name)
            if python_child is not None:
                python_child, fndata = python_child
                break
        else:
            for pymod, _ in python_objects:
                python_child = getattr(pymod, c_name, None)
                if python_child is not None:
                    break

        method_output = compare_function(python_child, fndata, c_method, True, filename)

        #Collect errors
        output["ignored_errors"] += method_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += len(method_output["errors"])
            method_output["ignored"] = True
        else:
            output["errors"] += len(method_output["errors"])
        output["methods"].append(method_output)
        
    # Scan variables (TODO)
    #for c_variable in header.variables:
    #    pass

def compare_class(python_object, c_object, filename):
    """
    Compares python_object and c_object recursively, and returns a summary of the differences.
    """
    #Put together dictionary of info
    output = {}
    output["filename"] = filename
    output["name"] = c_object["name"]
    output["present"] = python_object is not None
    output["errors"] = []
    output["ignored_errors"] = 0
    output["ignored"] = False

    #Check for not_implemented flags in the docstring
    children_to_ignore = parse_docstring(python_object.__doc__)

    #Compare all subclasses
    output["classes"] = list()
    for c_subclass in c_object["nested_classes"]:

        #Figure out the python child's name.
        python_subclass_name = c_subclass["name"]
        if python_object is None:
            python_subclass_name = ""

        #Figure out if we should ignore it
        ignore_child = python_subclass_name in children_to_ignore

        #Try to get the python child
        python_subclass = None
        if hasattr(python_object, python_subclass_name):
            python_subclass = getattr(python_object, python_subclass_name)

        #Compare the subclass
        subclass_output = compare_class(python_subclass, c_subclass, filename)

        #Collect errors from subclass before saving it
        output["ignored_errors"] += subclass_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += len(subclass_output["errors"])
            subclass_output["ignored"] = True
        else:
            output["errors"] += subclass_output["errors"]

        output["classes"].append(subclass_output)

    output["methods"] = list()
    for c_method in c_object["methods"]["public"]:

        #Figure out the python method's name.
        python_method_name = c_method["name"]
        if python_object is None:
            python_method_name = ""

        #Figure out if we should ignore it
        ignore_child = python_method_name in children_to_ignore

        #Try to get the child
        python_method = None
        if hasattr(python_object, python_method_name):
            python_method = getattr(python_object, python_method_name)

        #Compare the method.
        method_output = compare_function(python_method, None, c_method, False, filename)

        #Collect errors from the comparison
        output["ignored_errors"] += method_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += len(method_output["errors"])
            method_output["ignored"] = True
        else:
            output["errors"] += method_output["errors"]

        output["methods"].append(method_output)
    return output


def compare_function(python_object, fndata, c_object, check_fndata, filename):
    """
    Compares python_object and c_object, and returns a summary of the differences.
    """
    
    #Put together dictionary of front output info
    output = {}
    output["filename"] = filename
    output["name"] = c_object["name"]
    output["present"] = python_object is not None
    output["errors"] = []
    output["ignored_errors"] = 0
    output["ignored"] = False

    #Get all parameters
    output["parameters"] = c_object["parameters"][:]
    
    # Elide void parameters
    if len(output["parameters"]) == 1 and output["parameters"][0]["raw_type"] == "void": 
        output["parameters"] = []
    
    #And the return value
    output['returns'] = c_object['returns']
    output['returns_pointer'] = True if c_object['returns_pointer'] else False

    #Check if the corresponding python object has enough arguments to match
    if output["present"]:
        if check_fndata:
            fndata = getattr(python_object, 'fndata', None)
            if fndata is None:
                output['errors'].append('fndata not found')
            else:
                if output['name'] != fndata.c_name:
                    err = 'name does not match! (py: %s/%s, c: %s)' % (fndata.c_name, fndata.name, output['name'])
                    output['errors'].append(err)
                
                if len(fndata.params) != len(output['parameters']):
                    err = 'expected %s params, got %s' % (len(fndata.params), len(output['parameters']))
                    output['errors'].append(err)
        else:
            args, varargs, keywords, _ = inspect.getargspec(python_object)
            if varargs is None and keywords is None:
                args = [a for a in args if a != "self"]
                if len(args) != len(output["parameters"]):
                    err = 'expected %s params, got %s' % (len(args), len(output['parameters']))
                    output['errors'].append(err)
    
    return output

def _get_c_typeinfo(typename, c_pointer):
    
    c_type_name = translate_obj(typename)

    #Workaround for typedefed pointers
    if c_type_name in ["MUTEX_ID", "MULTIWAIT_ID"]:
        c_pointer = True

    #Check for pointers
    if c_pointer:
        if c_type_name.startswith("::"):
            c_type_name = c_type_name[2:]
            
    return c_type_name, c_pointer
    

def _get_py_typeinfo(py_param):
    
    #Check py param pointer
    if py_param.__class__.__name__ == "PyCPointerType":
        py_pointer = True
        py_type_obj = py_param._type_
    elif py_param.__class__.__name__ == "PyCFuncPtrType":
        py_pointer = True
        py_type_obj = py_param
    elif hasattr(py_param, "fake_pointer"):
        py_pointer = True
        py_type_obj = py_param
    else:
        py_pointer = False
        py_type_obj = py_param
    
    if hasattr(py_type_obj, "_type_"):
        # deal with char*
        if py_type_obj._type_ in ['z', 'P']:
            py_pointer = True
        py_type_name = translate_obj(py_type_obj._type_)
    else:
        py_type_name = type(py_type_obj).__name__
        if py_type_name == "type":
            py_type_name = py_type_obj.__name__
    
    return py_type_name, py_pointer

def scan_c_end(python_objects, summary):
    """
    Scans python_object for c function calls and compares them to the specifications in summary
    :param python_object: The python object to scan for c function calls
    :param summary: The output of compare_header_dirs for python_object
    """
    
    return [_scan_c_end(python_object, idx, summary) \
                for python_object, idx in python_objects]

def _scan_c_end(python_object, idx, summary):

    if idx is None:
        idx = index_py_obj(python_object)

    output = dict()
    output["errors"] = 0
    output["ignored_errors"] = 0
    output["name"] = python_object.__name__
    output["present"] = summary is not None
    output["methods"] = list()
    output["contains_methods"] = False
    output["classes"] = list()

    if not output["present"]:
        return output

    # Scan functions
    for _, (_, fndata) in idx['functions'].items():

        #Find c object
        c_object = None
        fname = ''
        for m in summary["methods"]:
            if m["name"] == fndata.c_name:
                c_object = m
                fname = m['filename']
                break

        #Put together dictionary of info
        method_summary = dict()
        method_summary["present"] = c_object is not None
        method_summary["name"] = fndata.c_name
        method_summary["filename"] = fname
        method_summary["errors"] = []
        method_summary["ignored_errors"] = 0
        if not method_summary["present"]:
            method_summary["errors"].append("missing c object")
        method_summary["ignored"] = False
        method_summary["parameters"] = list()
        
        if method_summary["present"]:
            
            # check the return type to see if it matches
            if fndata.restype is None:
                py_rettype_name = 'void'
                py_retpointer = False
            else:
                py_rettype_name, py_retpointer = _get_py_typeinfo(fndata.restype)
                
            c_rettype_name, c_retpointer = _get_c_typeinfo(c_object['returns'],
                                                           c_object['returns_pointer'])
                
            if py_retpointer != c_retpointer:
                method_summary['errors'].append("mismatched return ptr")
                
            if py_rettype_name != c_rettype_name and c_rettype_name != "void":
                method_summary["errors"].append("mismatched return type")
            
            method_summary['returns'] = c_object['returns']
            if c_object['returns_pointer']:
                method_summary['returns'] += ' *'
            
            method_summary["parameters"] = c_object["parameters"]

            if len(fndata.params) != len(c_object["parameters"]):
                err = 'expected %s params, got %s' % (len(fndata.params), len(c_object['parameters']))
                method_summary["errors"].append(err)

            for i in range(min(len(fndata.params), len(c_object["parameters"]))):

                c_param = c_object["parameters"][i]
                py_param = fndata.params[i][1]
                c_pointer = False
                py_pointer = False
                c_type_obj = None
                c_type_name = ""
                py_type_name = ""

                #Check for pointers
                if c_param["pointer"] != 0:
                    c_pointer = True
                else:
                    c_pointer = False

                if "raw_type" in c_param:
                    c_type_obj = c_param["raw_type"]
                else:
                    c_type_obj = c_param["type"]

                c_type_name, c_pointer = _get_c_typeinfo(c_type_obj, c_pointer)
                py_type_name, py_pointer = _get_py_typeinfo(py_param)

                # TODO: function pointers are weird
                if py_type_name == 'PyCFuncPtrType':
                    if 'function' in c_type_name.lower():
                        continue
                    
                    if c_pointer == True:
                        # TODO: need deeper validation, but.. hard
                        continue

                    method_summary['errors'].append("mismatched function pointer for '%s'" % c_param['name'])

                else:
                    if py_pointer != c_pointer:
                        method_summary["errors"].append("mismatched pointer for '%s'" % c_param['name'])
                        continue
                    
                    if py_type_name != c_type_name and c_type_name != "void":
                        method_summary["errors"].append("mismatched type for '%s'" % c_param['name'])
                        continue

        #Collect errors from the comparison
        output["errors"] += len(method_summary["errors"])

        output["methods"].append(method_summary)

    # Scan classes
    for cname, cls in idx['classes'].items():
        
        #Find c object
        c_object = None
        for m in summary["classes"]:
            if m["name"] == cname:
                c_object = m
                break

        class_summary = _scan_c_end(cls, None, c_object)

        if not class_summary["contains_methods"]:
            continue

        output["containes_methods"] = True

        #Collect errors from the comparison
        output["ignored_errors"] += class_summary["ignored_errors"]
        if class_summary["present"]:
            output["ignored_errors"] += class_summary["errors"]
            class_summary["ignored"] = True
        else:
            output["errors"] += class_summary["errors"]

        output["classes"].append(class_summary)

    return output

_translate_obj_aliases = [
   ["int32", "int", "i", "int32_t", "c_int", 'CTR_Code'],
   ["double", "d", "c_double"],
   ["float", "f", "c_float"],
   ["char", "z"],
   ["void", "P"],
   ["int8", "int8_t", "c_int8", "b"],
   ["uint8", "uint8_t", "c_uint8", "B"],
   ["int16", "int16_t", "c_int16", "h", "c_short", "c_short_t", "short"],
   ["uint16", "uint16_t", "c_uint16", "H", "c_ushort", "c_ushort_t", "unsigned short"],
   ["uint32", "uint", "u", "c_uint", "I", "uint32_t"],
   ["uint64", "uint64_t", "c_uint64", "int64", "int64_t", "c_int64", "long", "l", "L", "longlong", "c_long", "long_t"],
   ["bool", "?", "HAL_Bool"]
]

def translate_obj(obj):
    """
    Find the standard term for obj
    :param obj: A string name of a c type
    :returns The standard term for obj
    """
    
    for alias in _translate_obj_aliases:
        if obj in alias:
            return alias[0]
    return obj

_translate_c_aliases = {
    'void': ('None', False),
    'int64_t': ('C.c_int64', False),
    'uint64_t': ('C.c_uint64', False),
    'int32_t': ('C.c_int32', False),
    'uint32_t': ('C.c_uint32', False),
    'int8_t': ('C.c_int8', False),
    'uint8_t': ('C.c_uint8', False),
    'int': ('C.c_int', False),
    'bool': ('C.c_bool', False),
    'double': ('C.c_double', False),
    'float': ('C.c_float', False),
    'char': ('C.c_char', False),
    'HAL_Bool': ('C.c_bool', False), 
}

def __translate_c_aliases_ptrs():
    ptrs = {}
    for k, v in _translate_c_aliases.items():
        ptrs['%s *' % k] = ('C.POINTER(%s)' % v[0], True)
        
    _translate_c_aliases.update(ptrs)

__translate_c_aliases_ptrs()

def translate_c_to_py(obj):
    return _translate_c_aliases.get(obj, (obj, False))
    

def parse_docstring(docstring):
    '''
        Finds RST comments that indicate some functions should be ignored. To
        indicate such a function, use the following syntax::

            .. not_implemented: fn1, fn2, fn3

    '''
    ignore_comment = ".. not_implemented:"
    ignores = list()
    if docstring is not None:
        for line in docstring.split("\n"):
            line = line.strip()
            if line.startswith(ignore_comment):
                ignore_fns = line[len(ignore_comment):].strip()
                ignores.extend(fn.strip() for fn in ignore_fns.split(","))
    return ignores

def get_status_msg(summary):

    #Figure out what the status message and color should be for the
    status_message = list()
    if summary["present"]:
        status_message.append("Present")
        status_color = "green"
    else:
        # Don't mark this as an error, just a warning
        status_message.append("Not Present")
        status_color = "orange"

    if len(summary["errors"]) > 0:
        status_message.append("{} Error(s): {}".format(len(summary["errors"]),
                                                       summary["errors"]))
        status_color = "red"

    if summary["ignored_errors"] > 0:
        status_message.append("{} Ignored Error(s)".format(summary["ignored_errors"]))

    if summary["ignored"]:
        status_message.append("All Errors Ignored")
        if status_color == "red":
            status_color = "orange"

    return ", ".join(status_message), status_color


def stringize_class_summary(summary):
    output = list()

    status_message, status_color = get_status_msg(summary)

    #Print out title bar and status message
    output.append({"text": "", "color": ""})
    output.append({"text": class_start.format(summary["name"]), "color": ""})
    output.append({"text": status_message, "color": status_color})

    #If the class is present, handle the children
    if summary["present"]:

        #Get all methods.

        if len(summary["methods"]) != 0:

            #This is to figure out if we can hide the methods, if none of them are red.
            methods_match = True
            method_buffer = list()

            #Print the header to a buffer
            method_buffer.append({"text": "", "color": ""})
            method_buffer.append({"text": "Methods:", "color": ""})
            method_buffer.append({"text": "", "color": ""})

            #Recurse for all of the methods
            for f in summary["methods"]:
                for t in stringize_method_summary(f):
                    if t["color"] == "red":
                        t["text"] = arrowtab + t["text"]
                        methods_match = False
                    else:
                        t["text"] = tab + t["text"]
                    method_buffer.append(t)

            #Print a final space
            method_buffer.append({"text": "", "color": ""})

            #If we can hide the methods, just print out a summary. Otherwise extend output with method_buffer.
            if methods_match:
                output.append({"text": "All methods are either correct or ignored, hiding {} methods".format(len(summary["methods"])), "color": "green"})
            else:
                output.extend(method_buffer)

        if len(summary["classes"]) != 0:

            #This is to figure out if we can hide the subclasses, if none of them are red.
            subclasses_match = True
            subclass_buffer = list()

            #Print the header to the buffer
            subclass_buffer.append({"text": "", "color": ""})
            subclass_buffer.append({"text": "Subclasses:", "color": ""})

            #Recurse for all of the classes
            for f in summary["classes"]:
                for t in stringize_class_summary(f):
                    t["text"] = tab + t["text"]
                    if t["color"] == "red":
                        subclasses_match = False
                    subclass_buffer.append(t)

            #Print a final space
            subclass_buffer.append({"text": "", "color": ""})

            #If we can hide the subclasses, just print out a summary. Otherwise extend output with subclass_buffer.
            if subclasses_match:
                output.append({"text": "All sub-classes are either correct or ignored, hiding {} sub-classes".format(len(summary["classes"])), "color": "green"})
            else:
                output.extend(subclass_buffer)
    return output


def stringize_method_summary(summary):

    status_message, status_color = get_status_msg(summary)

    arguments = "(" + ", ".join(arg["type"] + " " + arg["name"] for arg in summary["parameters"]) + ")"
    text = ''
    if 'returns' in summary:
        text = summary['returns'] + ' '
    text += summary["name"] + arguments + " " + status_message
    ret = [{"text": text, "color": status_color, 'filename': summary['filename']}, ]
    return ret

def c_fn_name_to_py(n):
    # returns name, c_name
    if n.startswith('HAL_'):
        return n[4].lower() + n[5:], None
    else:
        return n, n

def stringize_method_to_hal(summary):
    
    functype = '_RETFUNC'
    name, c_name = c_fn_name_to_py(summary['name'])
    retval = summary.get('returns')
    params = summary['parameters'][:]
    
    if retval == 'CTR_Code':
        functype = '_CTRFUNC'
        params = params[1:]
    elif len(params) and params[-1]['name'] == 'status':
        functype = '_STATUSFUNC'
        params.pop()
    
    text = name + ' = ' + functype + '("' + name + '"'
    
    if retval != 'CTR_Code':
        if retval:
            text += ', ' + translate_c_to_py(retval)[0]
        else:
            text += ', None'
    
    ptrs = []
    
    for arg in params:
        argtype, is_ptr = translate_c_to_py(arg['type'])
        text += ', ("' + arg['name'] + '", ' + argtype + ')'
        
        if is_ptr:
            ptrs.append(arg['name'])
        
    if len(ptrs):
        text += ', out=["' + '", "'.join(ptrs) + '"]'
    
    if c_name:
        text += ', c_name="%s"' % c_name
    
    text += ")"
    
    return [{'text': text, 'filename': summary['filename']}] 

def stringize_method_to_halsim(summary):
    
    name, _ = c_fn_name_to_py(summary['name'])
    
    text = 'def ' + name + '(' + \
            ', '.join(arg['name'] for arg in summary['parameters']) + '):'
    
    text += '\n    assert False'
    text += '\n'
    
    return [{'text': text, 'filename': summary['filename']}] 

def stringize_text(text):
    return {'text': text}

def sort_by_fname(l):
    return sorted(l, key=lambda i: i['filename'])

def print_list(inp):
    """
    :param inp: A list of {"text": "", "color": ""} values, corresponding to lines of text
    Prints inp as colored text.
    """
    #For each
    
    last_filename = None
    
    for text in inp:
        filename = text.get('filename')
        if filename:
            if last_filename != filename:
                print("\n", filename)
            
            last_filename = filename
        
        color = text.get('color')
        if color == "green":
            print(green_head + text["text"] + end_head)
        elif color == "red":
            print(red_head + text["text"] + end_head)
        elif color == "orange":
            print(orange_head + text["text"] + end_head)
        else:
            print(text["text"])


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('hal_dir')
    parser.add_argument('check_type', type=str, choices=['all', 'c', 'py'])
    parser.add_argument('filter', type=str, default=None, nargs='?',
                        help="Only process this filename")
    
    parser.add_argument('--nostrict', action='store_true', default=False)
    parser.add_argument('--stubs', type=str, choices=['no', 'pyhal', 'halsim'], default='no',
                        help="Use pyhal/halsim to generate stubs")
    
    args = parser.parse_args()
    
    if args.nostrict:
        os.environ['HAL_NOSTRICT'] = '1'
    
    # Guarantee that this is being ran on the current source tree
    sys.path.insert(0, join(dirname(__file__), '..', '..', '..', 'hal-base'))
    try:
        import hal
    except AttributeError:
        print("Note: you may want to specify --nostrict to avoid seeing this error")
        print()
        raise
    
    python_objects = index_py_funcs([hal])
 
    py_end_output = compare_header_dirs(python_objects, get_hal_dirs(args.hal_dir), args.filter)
    # TODO: eventually support multiple objects...
    c_end_output = scan_c_end(python_objects, py_end_output)[0]
    
    if args.check_type in ['all', 'c']:
        print("\n\n\n")
        print(equals_bar + "=================" + equals_bar)
        print(equals_bar + "HAL C Definitions" + equals_bar)
        print(equals_bar + "=================" + equals_bar)
        print()
        print("For each HAL function defined in a C/C++ header file, check")
        print("to see if there is a defined python function.")
        print()
        
        text_list = list()
        for method in sort_by_fname(py_end_output["methods"]):
            if method['present'] or args.stubs == 'no':
                text_list += stringize_method_summary(method)
                
            if not method['present']:
                if args.stubs == 'pyhal':
                    text_list += stringize_method_to_hal(method)
                if args.stubs == 'halsim':
                    text_list += stringize_method_to_halsim(method)
        
        for cls in sort_by_fname(py_end_output["classes"]):
            text_list.extend(stringize_class_summary(cls))
        print_list(text_list)

    if args.check_type in ['all', 'py']:
        print("\n\n\n")
        print(equals_bar + "======================" + equals_bar)
        print(equals_bar + "Python HAL definitions" + equals_bar)
        print(equals_bar + "======================" + equals_bar)
        print()
        print("For each Python definition of a HAL function, check its method signature")
        print("against the C API and verify that it is correct.")
        print()
        print("This output should be 100% correct, as errors here can potentially")
        print("cause segfaults.")
        print()
        
        text_list = list()
        for method in sort_by_fname(c_end_output["methods"]):
            text_list.extend(stringize_method_summary(method))
        for cls in sort_by_fname(c_end_output["classes"]):
            text_list.extend(stringize_class_summary(cls))
        print_list(text_list)
    
    # Print errors at the end, so we don't have to move the terminal
    print()
    print("C++ API: {} Errors, {} Ignored errors".format(py_end_output["errors"], py_end_output["ignored_errors"]))
    print("{} API:    {} Errors, {} Ignored errors".format(c_end_output['name'], c_end_output["errors"], c_end_output["ignored_errors"]))
    print()
    
