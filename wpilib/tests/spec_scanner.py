import os
import sys
import plyj.parser
import plyj.model as m
import inspect


plyj_parser = plyj.parser.Parser()

green_head = "\033[92m"
red_head = "\033[91m"
orange_head = "\033[93m"
end_head = "\033[0m"
dash_bar = "-----------------------"
class_start = dash_bar + "{}" + dash_bar
class_end = dash_bar + "End Class {}" + dash_bar
tab = "    "
arrowtab = "--> "


def scan_specifications(python_object, java_dirs):
    """
    Parses through java_dirs and matches java objects to objects in
    python_object and returns a summary of it's findings.
    """

    output = list()

    #Get all java files in java_dirs
    java_files = list()
    for dir in java_dirs:
        java_files.extend([os.path.join(dir, s) for s in os.listdir(dir)])

    #Get the :jscan ignore flags in the docstring of python_object
    children_to_ignore = parse_docstring(python_object.__doc__)

    #For every java file
    for java_file in java_files:

        #Make sure it is an actual .java file.
        if os.path.splitext(java_file)[1] != ".java":
            continue

        #For each java type declaration
        tree = plyj_parser.parse_file(java_file)
        for java_child in tree.type_declarations:
            #Make sure it is something of interest
            if not isinstance(java_child, m.ClassDeclaration) and not isinstance(java_child, m.MethodDeclaration) and\
                    not isinstance(java_child, m.ConstructorDeclaration):
                continue

            #Do we ignore?
            ignore_child = java_child.name in children_to_ignore

            #Get the first python object and compare!
            python_child = None
            if hasattr(python_object, java_child.name):
                python_child = getattr(python_object, java_child.name)
            output.append(compare_object(python_child, java_child, ignore_child))
    return output


def compare_object(python_object, java_object, ignored=False):
    """
    Compares python_object and java_object recursively, and returns a summary of the differences.
    """
    #Put together dictionary of info
    output = {}
    output["name"] = java_object.name
    output["present"] = python_object is not None
    output["matches"] = output["present"]
    output["type"] = java_object.__class__.__name__
    output["ignored"] = ignored

    #If it is a method, get it's parameters.
    if isinstance(java_object, m.MethodDeclaration) or isinstance(java_object, m.ConstructorDeclaration):
        #Get all parameters
        output["parameters"] = list()
        for p in java_object.parameters:
            if isinstance(p.type, str):
                output["parameters"].append({"type": p.type, "name": p.variable.name})
            elif isinstance(p.type.name, str):
                output["parameters"].append({"type": p.type.name, "name": p.variable.name})
            else:
                output["parameters"].append({"type": p.type.name.value, "name": p.variable.name})

        #Check if the corresponding python object has enough arguments to match
        if output["present"]:
            args, varargs, keywords, defaults = inspect.getargspec(python_object)
            if varargs is None and keywords is None:
                args = [a for a in args if a != "self"]
                if len(args) < len(output["parameters"]):
                    output["matches"] = False

    elif isinstance(java_object, m.ClassDeclaration):
        #Check for :jscan ignore flags in the docstring
        children_to_ignore = parse_docstring(python_object.__doc__)
        #Get all children
        output["children"] = list()
        for java_child in java_object.body:

            #Check if the child is of interest.
            if not isinstance(java_child, m.ClassDeclaration) and not isinstance(java_child, m.MethodDeclaration)\
                    and not isinstance(java_child, m.ConstructorDeclaration):
                continue

            #Figure out the python child's name.
            python_child_name = java_child.name
            if python_object is None:
                python_child_name = ""
            elif isinstance(java_child, m.ConstructorDeclaration):
                python_child_name = "__init__"

            #Figure out if we should ignore it
            ignore_child = python_child_name in children_to_ignore

            #Try to get the child
            python_child = None
            if hasattr(python_object, python_child_name):
                python_child = getattr(python_object, python_child_name)

            #Compare the child and set our matches variable from it.
            child_output = compare_object(python_child, java_child, ignore_child)
            if not child_output["matches"] and not ignore_child:
                output["matches"] = False
            output["children"].append(child_output)
    return output


def parse_docstring(docstring):
    ignores = list()
    if docstring is not None:
        for line in docstring.split("\n"):
            split = line.split(":jscan ignore")
            if len(split) > 1:
                ignores.append(split[1].strip(" "))
    return ignores


def stringize_summary(summary):

    output = []

    if not summary["present"]:
        status_message = "Not Present"
        status_color = "red"
    elif not summary["matches"]:
        status_message = "Present, but incorrect"
        status_color = "red"
    else:
        status_message = "Present and Correct"
        status_color = "green"

    if summary["ignored"]:
        status_message += " - Ignored"
        if status_color == "red":
            status_color = "orange"

    #For classes:
    if summary["type"] == "ClassDeclaration":

        #Print out title bar and status message
        output.append({"text": "", "color": ""})
        output.append({"text": class_start.format(summary["name"]), "color": ""})
        output.append({"text": status_message, "color": status_color})

        #If the element is present, handle the children
        if summary["present"]:

            #Get all children that are methods.
            methods = [cl for cl in summary["children"] if cl["type"] == "MethodDeclaration" or cl["type"] == "ConstructorDeclaration"]
            if len(methods) != 0:
                methods_match = True
                method_buffer = []
                method_buffer.append({"text": "", "color": ""})
                method_buffer.append({"text": "Methods:", "color": ""})
                method_buffer.append({"text": "", "color": ""})
                for f in methods:
                    for t in stringize_summary(f):
                        if t["color"] == "red":
                            t["text"] = arrowtab + t["text"]
                            methods_match = False
                        else:
                            t["text"] = tab + t["text"]
                        method_buffer.append(t)
                method_buffer.append({"text": "", "color": ""})

                if methods_match:
                    output.append({"text": "All methods are either correct or ignored, hiding {} methods".format(len(methods)), "color": "green"})
                else:
                    output.extend(method_buffer)

            subclasses = [cl for cl in summary["children"] if cl["type"] == "ClassDeclaration"]
            if len(subclasses) != 0:
                subclasses_match = True
                subclass_buffer = list()
                subclass_buffer.append({"text": "", "color": ""})
                subclass_buffer.append({"text": "Subclasses:", "color": ""})
                for f in subclasses:
                    for t in stringize_summary(f):
                        t["text"] = tab + t["text"]
                        if t["color"] == "red":
                            subclasses_match = False
                        subclass_buffer.append(t)
                subclass_buffer.append({"text": "", "color": ""})

                if subclasses_match:
                    output.append({"text": "All sub-classes are either correct or ignored, hiding {} sub-classes".format(len(subclasses)), "color": "green"})
                else:
                    output.extend(subclass_buffer)

    elif summary["type"] == "MethodDeclaration" or summary["type"] == "ConstructorDeclaration":
        arguments = "(" + ", ".join(arg["type"] + " " + arg["name"] for arg in summary["parameters"]) + ")"
        text = summary["name"] + arguments + " " + status_message
        output.append({"text": text, "color": status_color})

    return output


def print_list(inp):
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
    import wpilib

    output = scan_specifications(wpilib, sys.argv[1:])
    text_list = list()
    for item in output:
        text_list.extend(stringize_summary(item))
    print_list(text_list)
