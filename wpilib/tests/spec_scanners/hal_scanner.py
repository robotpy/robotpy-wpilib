import os
from os.path import dirname, join
import sys
import CppHeaderParser
import inspect

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


def compare_header_dirs(python_object, header_dirs):
    """
    Parses through cpp_dirs and matches c++ header objects to front-end objects in
    python_object and returns a summary of it's findings.
    """

    output = dict()
    output["errors"] = 0
    output["ignored_errors"] = 0
    output["methods"] = list()
    output["classes"] = list()

    #Get all header files in header_dirs
    header_files = list()
    for dir in header_dirs:
        header_files.extend([os.path.join(dir, s) for s in os.listdir(dir)])

    #Get the .. not_implemented ignore flags in the docstring of python_object
    children_to_ignore = parse_docstring(python_object.__doc__)

    #For every header file
    for header_file in header_files:

        #Make sure it is a .hpp file
        if os.path.splitext(header_file)[1] != ".hpp":
            continue

        #For each class declaration
        header = CppHeaderParser.CppHeader(header_file)

        #Scan classes
        for c_class_name in header.classes:
            c_class = header.classes[c_class_name]
            #Do we ignore?
            ignore_child = c_class["name"] in children_to_ignore

            #Get the first python object and compare!
            python_child = None
            if hasattr(python_object, c_class["name"]):
                python_child = getattr(python_object, c_class["name"])

            class_output = compare_class(python_child, c_class)

            #Collect errors
            output["ignored_errors"] += class_output["ignored_errors"]
            if ignore_child:
                output["ignored_errors"] += class_output["errors"]
                class_output["ignored"] = True
            else:
                output["errors"] += class_output["errors"]
            output["classes"].append(class_output)

        #Scan methods
        for c_method in header.functions:
            #Do we ignore?
            ignore_child = c_method["name"] in children_to_ignore

            #Get the first python object and compare!
            python_child = None
            if hasattr(python_object, c_method["name"]):
                python_child = getattr(python_object, c_method["name"])

            method_output = compare_function(python_child, c_method)

            #Collect errors
            output["ignored_errors"] += method_output["ignored_errors"]
            if ignore_child:
                output["ignored_errors"] += method_output["errors"]
                method_output["ignored"] = True
            else:
                output["errors"] += method_output["errors"]
            output["methods"].append(method_output)

    return output

def compare_class(python_object, c_object):
    """
    Compares python_object and c_object recursively, and returns a summary of the differences.
    """
    #Put together dictionary of info
    output = {}
    output["name"] = c_object["name"]
    output["present"] = python_object is not None
    output["errors"] = 0
    output["ignored_errors"] = 0
    if not output["present"]:
        output["errors"] += 1
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
        subclass_output = compare_class(python_subclass, c_subclass)

        #Collect errors from subclass before saving it
        output["ignored_errors"] += subclass_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += subclass_output["errors"]
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
        method_output = compare_function(python_method, c_method)

        #Collect errors from the comparison
        output["ignored_errors"] += method_output["ignored_errors"]
        if ignore_child:
            output["ignored_errors"] += method_output["errors"]
            method_output["ignored"] = True
        else:
            output["errors"] += method_output["errors"]

        output["methods"].append(method_output)
    return output


def compare_function(python_object, c_object):
    """
    Compares python_object and c_object, and returns a summary of the differences.
    """
    
    #Put together dictionary of front output info
    output = {}
    output["name"] = c_object["name"]
    output["present"] = python_object is not None
    output["errors"] = 0
    output["ignored_errors"] = 0
    if not output["present"]:
        output["errors"] += 1
    output["ignored"] = False

    #Get all parameters
    output["parameters"] = c_object["parameters"][:]
    
    #And the return value
    output['returns'] = c_object['returns']
    output['returns_pointer'] = True if c_object['returns_pointer'] else False

    #Check if the corresponding python object has enough arguments to match
    if output["present"]:
        args, varargs, keywords, defaults = inspect.getargspec(python_object)
        if varargs is None and keywords is None:
            args = [a for a in args if a != "self"]
            if len(args) < len(output["parameters"]):
                output["errors"] += 1
    
    return output

def _get_c_typeinfo(typename, c_pointer):
    
    c_type_name = translate_obj(typename)

    #Workaround for typedefed pointers
    if c_type_name in ["MUTEX_ID", "SEMAPHORE_ID", "MULTIWAIT_ID"]:
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
    elif hasattr(py_param, "fake_pointer"):
        py_pointer = True
        py_type_obj = py_param
    else:
        py_pointer = False
        py_type_obj = py_param

    if hasattr(py_type_obj, "_type_"):
        py_type_name = translate_obj(py_type_obj._type_)
    else:
        py_type_name = type(py_type_obj).__name__
        if py_type_name == "type":
            py_type_name = py_type_obj.__name__
            
    return py_type_name, py_pointer

def scan_c_end(python_object, summary):
    """
    Scans python_object for c function calls and compares them to the specifications in summary
    :param python_object: The python object to scan for c function calls
    :param summary: The output of compare_header_dirs for python_object
    """

    output = dict()
    output["errors"] = 0
    output["ignored_errors"] = 0
    output["name"] = python_object.__name__
    output["present"] = summary is not None
    output["methods"] = list()
    output["contains_methods"] = False
    output["classes"] = list()

    if not output["present"]:
        output["errors"] += 1
        return output

    #Get the module class
    for name, obj in inspect.getmembers(python_object):
        if hasattr(obj, "fndata"):

            #Get fndata
            name, restype, params, out = obj.fndata


            #Find c object
            c_object = None
            for m in summary["methods"]:
                if m["name"] == name:
                    c_object = m
                    break

            #Put together dictionary of info
            method_summary = dict()
            method_summary["present"] = c_object is not None
            method_summary["name"] = name
            method_summary["errors"] = 0
            method_summary["ignored_errors"] = 0
            if not method_summary["present"]:
                method_summary["errors"] += 1
            method_summary["ignored"] = False
            method_summary["parameters"] = list()
            
            if method_summary["present"]:
                
                # check the return type to see if it matches
                if restype is None:
                    py_rettype_name = 'void'
                    py_retpointer = False
                else:
                    py_rettype_name, py_retpointer = _get_py_typeinfo(restype)
                    
                c_rettype_name, c_retpointer = _get_c_typeinfo(c_object['returns'],
                                                               c_object['returns_pointer'])
                    
                if py_retpointer != c_retpointer:
                    method_summary['errors'] += 1
                    
                if py_rettype_name != c_rettype_name and c_rettype_name != "void":
                    method_summary["errors"] += 1
                    
                if method_summary['errors'] != 0:
                    print(method_summary['name'])
                    print(py_rettype_name, py_retpointer)
                    print(c_rettype_name, c_retpointer)
                    exit(1)
                
                method_summary['returns'] = c_object['returns']
                if c_object['returns_pointer']:
                    method_summary['returns'] += ' *'
                
                method_summary["parameters"] = c_object["parameters"]

                if len(params) != len(c_object["parameters"]):
                    method_summary["errors"] += abs(len(params) - len(c_object["parameters"]))

                for i in range(min(len(params), len(c_object["parameters"]))):

                    c_param = c_object["parameters"][i]
                    py_param = params[i][1]
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

                    if py_pointer != c_pointer:
                        method_summary["errors"] += 1
                        continue

                    if py_type_name != c_type_name and c_type_name != "void":
                        method_summary["errors"] += 1
                        continue

            #Collect errors from the comparison
            output["errors"] += method_summary["errors"]

            output["methods"].append(method_summary)

        if inspect.isclass(obj):
            #Find c object
            c_object = None
            for m in summary["classes"]:
                if m["name"] == name:
                    c_object = m
                    break

            class_summary = scan_c_end(obj, c_object)

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

def translate_obj(obj):
    """
    Find the standard term for obj
    :param obj: A string name of a c type
    :returns The standard term for obj
    """
    aliases = [["int32", "int", "i", "int32_t", "c_int"],
               ["double", "d", "c_double"],
               ["float", "f", "c_float"],
               ["int8", "int8_t", "c_int8", "b"],
               ["uint8", "uint8_t", "c_uint8", "B"],
               ["int16", "int16_t", "c_int16", "h", "c_short", "c_short_t", "short"],
               ["uint16", "uint16_t", "c_uint16", "H", "c_ushort", "c_ushort_t", "unsigned short"],
               ["uint32", "uint", "u", "c_uint", "I", "uint32_t"],
               ["uint64", "uint64_t", "c_uint64", "int64", "int64_t", "c_int64", "long", "l", "longlong", "c_long", "long_t"],
               ["bool", "?"]]
    for alias in aliases:
        if obj in alias:
            return alias[0]
    return obj

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
        status_message.append("Not Present")
        status_color = "red"

    if summary["errors"] > 0:
        status_message.append("{} Error(s)".format(summary["errors"]))
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
    return [{"text": text, "color": status_color}, ]

def print_list(inp):
    """
    :param inp: A list of {"text": "", "color": ""} values, corresponding to lines of text
    Prints inp as colored text.
    """
    #For each
    for text in inp:
        if text["color"] == "green":
            print(green_head + text["text"] + end_head)
        elif text["color"] == "red":
            print(red_head + text["text"] + end_head)
        elif text["color"] == "orange":
            print(orange_head + text["text"] + end_head)
        else:
            print(text["text"])


if __name__ == "__main__":

    # Guarantee that this is being ran on the current source tree
    sys.path.insert(0, join(dirname(__file__), '..', '..', '..', 'hal-base'))
    import hal

    if len(sys.argv) == 1:
        print("Usage: python hal_scanner.py hal_path")
        exit(1)

    HAL_path = join(sys.argv[1], 'include', 'HAL')

    print("\n\n\n")
    print(equals_bar + "==============" + equals_bar)
    print(equals_bar + "Python HAL API" + equals_bar)
    print(equals_bar + "==============" + equals_bar)
    print()
    print("This compares the HAL API, what is directly used by the python wpilib,\n"
          "to the c++ API and reports errors for inconsistencies. These differences \n"
          "are often intentional, and errors shown here usually won't cause issues.")

    py_end_output = compare_header_dirs(hal, [HAL_path])

    print("\n{} Errors, {} Ignored errors \n\n".format(py_end_output["errors"], py_end_output["ignored_errors"]))

    text_list = list()
    for method in py_end_output["methods"]:
        text_list.extend(stringize_method_summary(method))
    for cls in py_end_output["classes"]:
        text_list.extend(stringize_class_summary(cls))
    print_list(text_list)

    print("\n\n\n")
    print(equals_bar + "=============" + equals_bar)
    print(equals_bar + "C++ HAL Usage" + equals_bar)
    print(equals_bar + "=============" + equals_bar)
    print()
    print("This checks the Python HAL's Usage of the C++ API, and reports errors for\n"
          "incorrect C++ API Calls, which would cause segmentation faults. This should\n"
          "be 100% correct, without errors.")

    c_end_output = scan_c_end(hal, py_end_output)

    print("\n{} Errors, {} Ignored errors \n\n".format(c_end_output["errors"], c_end_output["ignored_errors"]))


    text_list = list()
    for method in c_end_output["methods"]:
        text_list.extend(stringize_method_summary(method))
    for cls in c_end_output["classes"]:
        text_list.extend(stringize_class_summary(cls))
    print_list(text_list)
