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
class_start = dash_bar + "{}" + dash_bar
class_end = dash_bar + "End Class {}" + dash_bar
tab = "    "
arrowtab = "--> "


def compare_folders(python_object, header_dirs):
    """
    Parses through cpp_dirs and matches c++ header objects to objects in
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

    #Put together dictionary of info
    output = {}
    output["name"] = c_object["name"]
    output["present"] = python_object is not None
    output["errors"] = 0
    output["ignored_errors"] = 0
    if not output["present"]:
        output["errors"] += 1
    output["ignored"] = False

    #Get all parameters
    output["parameters"] = [p for p in c_object["parameters"]]

    #Check if the corresponding python object has enough arguments to match
    if output["present"]:
        args, varargs, keywords, defaults = inspect.getargspec(python_object)
        if varargs is None and keywords is None:
            args = [a for a in args if a != "self"]
            if len(args) < len(output["parameters"]):
                output["errors"] += 1

    return output


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
                output.append({"text": "All sub-classes are either correct or ignored, hiding {} sub-classes".format(len(summary["subclasses"])), "color": "green"})
            else:
                output.extend(subclass_buffer)
    return output


def stringize_method_summary(summary):

    status_message, status_color = get_status_msg(summary)

    arguments = "(" + ", ".join(arg["type"] + " " + arg["name"] for arg in summary["parameters"]) + ")"
    text = summary["name"] + arguments + " " + status_message
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
    sys.path.insert(0, join(dirname(__file__), '..'))
    import hal

    if len(sys.argv) == 1:
        print("Usage: python cpp_scanner.py hal_path")
        exit(1)

    HAL_path = join(sys.argv[1], 'include', 'HAL')

    output = compare_folders(hal, [HAL_path])
    text_list = list()
    for method in output["methods"]:
        text_list.extend(stringize_method_summary(method))
    for cls in output["classes"]:
        text_list.extend(stringize_class_summary(cls))
    print_list(text_list)

    print("\n{} Errors, {} Ignored errors ".format(output["errors"], output["ignored_errors"]))
