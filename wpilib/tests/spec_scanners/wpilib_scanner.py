import os
from os.path import dirname, join
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


def get_wpilib_dirs(wpilib_dir):
    paths = list()
    paths.append(
        join(wpilib_dir, "src", "main", "java", "edu", "wpi", "first", "wpilibj")
    )
    return paths


def get_python_attr(python_object, name):
    for name in [name, "_" + name]:
        if hasattr(python_object, name):
            return getattr(python_object, name)


def compare_folders(python_object, java_dirs):
    """
    Parses through java_dirs and matches java objects to objects in
    python_object and returns a summary of it's findings.
    """

    output = dict()
    output["errors"] = 0
    output["ignored_errors"] = 0
    output["children"] = list()

    # Get all java files in java_dirs
    java_files = list()
    for dir in java_dirs:
        java_files.extend([os.path.join(dir, s) for s in os.listdir(dir)])

    # Get the :jscan ignore flags in the docstring of python_object
    children_to_ignore = parse_docstring(python_object.__doc__)

    # For every java file
    for java_file in java_files:

        # Make sure it is an actual .java file.
        if os.path.splitext(java_file)[1] != ".java":
            continue

        # For each java type declaration
        tree = plyj_parser.parse_file(java_file)
        if tree is None:
            continue
        for java_child in tree.type_declarations:
            # Make sure it is something of interest
            if (
                not isinstance(java_child, m.ClassDeclaration)
                and not isinstance(java_child, m.MethodDeclaration)
                and not isinstance(java_child, m.ConstructorDeclaration)
            ):
                continue

            # Do we ignore?
            ignore_child = java_child.name in children_to_ignore

            # Get the first python object and compare!
            python_child = get_python_attr(python_object, java_child.name)

            child_output = compare_object(python_child, java_child)

            # Collect errors
            output["ignored_errors"] += child_output["ignored_errors"]
            if ignore_child:
                output["ignored_errors"] += child_output["errors"]
                child_output["ignored"] = True
            else:
                output["errors"] += child_output["errors"]
            output["children"].append(child_output)

    return output


def compare_object(python_object, java_object):
    """
    Compares python_object and java_object recursively, and returns a summary of the differences.
    """
    # Put together dictionary of info
    output = {}
    output["name"] = java_object.name
    output["present"] = python_object is not None
    output["errors"] = 0
    output["ignored_errors"] = 0
    if not output["present"]:
        output["errors"] += 1
    output["type"] = java_object.__class__.__name__
    output["ignored"] = False

    # If it is a method, get it's parameters.
    if isinstance(java_object, m.MethodDeclaration) or isinstance(
        java_object, m.ConstructorDeclaration
    ):
        # Get all parameters
        output["parameters"] = list()
        for p in java_object.parameters:
            if isinstance(p.type, str):
                output["parameters"].append({"type": p.type, "name": p.variable.name})
            elif isinstance(p.type.name, str):
                output["parameters"].append(
                    {"type": p.type.name, "name": p.variable.name}
                )
            else:
                output["parameters"].append(
                    {"type": p.type.name.value, "name": p.variable.name}
                )

        # Check if the corresponding python object has enough arguments to match
        if output["present"]:
            argspec = inspect.getfullargspec(python_object)
            if argspec.varargs is None and argspec.varkw is None:
                args = [a for a in argspec.args if a != "self"]
                if len(args) < len(output["parameters"]):
                    output["errors"] += 1

    elif isinstance(java_object, m.ClassDeclaration):
        # Check for not_implemented flags in the docstring
        children_to_ignore = parse_docstring(python_object.__doc__)
        # Get all children
        output["children"] = list()
        for java_child in java_object.body:

            # Check if the child is of interest.
            if (
                not isinstance(java_child, m.ClassDeclaration)
                and not isinstance(java_child, m.MethodDeclaration)
                and not isinstance(java_child, m.ConstructorDeclaration)
            ):
                continue

            # Figure out the python child's name.
            python_child_name = java_child.name
            if python_object is None:
                python_child_name = ""
            elif isinstance(java_child, m.ConstructorDeclaration):
                python_child_name = "__init__"

            # Figure out if we should ignore it
            ignore_child = python_child_name in children_to_ignore

            # Try to get the child
            python_child = get_python_attr(python_object, python_child_name)

            # Compare the child and set our matches variable from it.
            child_output = compare_object(python_child, java_child)

            # Collect errors from children
            output["ignored_errors"] += child_output["ignored_errors"]
            if ignore_child:
                output["ignored_errors"] += child_output["errors"]
                child_output["ignored"] = True
            else:
                output["errors"] += child_output["errors"]

            output["children"].append(child_output)
    return output


def parse_docstring(docstring):
    """
        Finds RST comments that indicate some functions should be ignored. To
        indicate such a function, use the following syntax::

            .. not_implemented: fn1, fn2, fn3

    """
    ignore_comment = ".. not_implemented:"
    ignores = list()
    if docstring is not None:
        for line in docstring.split("\n"):
            line = line.strip()
            if line.startswith(ignore_comment):
                ignore_fns = line[len(ignore_comment) :].strip()
                ignores.extend(fn.strip() for fn in ignore_fns.split(","))
    return ignores


def stringize_summary(summary):
    """
    :param summary: a single comparison summary dictionary, as output by compare_object().
    :returns A list of {"text": "", "color": ""} values, corresponding to lines of text.
    """
    output = list()

    # Figure out what the status message and color should be for the
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

    # For classes:
    if summary["type"] == "ClassDeclaration":

        # Print out title bar and status message
        output.append({"text": "", "color": ""})
        output.append({"text": class_start.format(summary["name"]), "color": ""})
        output.append({"text": ", ".join(status_message), "color": status_color})

        # If the element is present, handle the children
        if summary["present"]:

            # Get all children that are methods.
            methods = [
                cl
                for cl in summary["children"]
                if cl["type"] == "MethodDeclaration"
                or cl["type"] == "ConstructorDeclaration"
            ]
            if len(methods) != 0:

                # This is to figure out if we can hide the methods, if none of them are red.
                methods_match = True
                method_buffer = list()

                # Print the header to a buffer
                method_buffer.append({"text": "", "color": ""})
                method_buffer.append({"text": "Methods:", "color": ""})
                method_buffer.append({"text": "", "color": ""})

                # Recurse for all of the methods
                for f in methods:
                    for t in stringize_summary(f):
                        if t["color"] == "red":
                            t["text"] = arrowtab + t["text"]
                            methods_match = False
                        else:
                            t["text"] = tab + t["text"]
                        method_buffer.append(t)

                # Print a final space
                method_buffer.append({"text": "", "color": ""})

                # If we can hide the methods, just print out a summary. Otherwise extend output with method_buffer.
                if methods_match:
                    output.append(
                        {
                            "text": "All methods are either correct or ignored, hiding {} methods".format(
                                len(methods)
                            ),
                            "color": "green",
                        }
                    )
                else:
                    output.extend(method_buffer)

            # Get all children that are classes.
            subclasses = [
                cl for cl in summary["children"] if cl["type"] == "ClassDeclaration"
            ]
            if len(subclasses) != 0:

                # This is to figure out if we can hide the subclasses, if none of them are red.
                subclasses_match = True
                subclass_buffer = list()

                # Print the header to the buffer
                subclass_buffer.append({"text": "", "color": ""})
                subclass_buffer.append({"text": "Subclasses:", "color": ""})

                # Recurse for all of the classes
                for f in subclasses:
                    for t in stringize_summary(f):
                        t["text"] = tab + t["text"]
                        if t["color"] == "red":
                            subclasses_match = False
                        subclass_buffer.append(t)

                # Print a final space
                subclass_buffer.append({"text": "", "color": ""})

                # If we can hide the subclasses, just print out a summary. Otherwise extend output with subclass_buffer.
                if subclasses_match:
                    output.append(
                        {
                            "text": "All sub-classes are either correct or ignored, hiding {} sub-classes".format(
                                len(subclasses)
                            ),
                            "color": "green",
                        }
                    )
                else:
                    output.extend(subclass_buffer)

    # For methods, just print it out in name(argument, argument, ...) syntax.
    elif (
        summary["type"] == "MethodDeclaration"
        or summary["type"] == "ConstructorDeclaration"
    ):
        arguments = (
            "("
            + ", ".join(
                arg["type"] + " " + arg["name"] for arg in summary["parameters"]
            )
            + ")"
        )
        text = summary["name"] + arguments + " " + ", ".join(status_message)
        output.append({"text": text, "color": status_color})

    return output


def print_list(inp):
    """
    :param inp: A list of {"text": "", "color": ""} values, corresponding to lines of text
    Prints inp as colored text.
    """
    # For each
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
    sys.path.insert(0, join(dirname(__file__), "..", ".."))
    import wpilib

    if len(sys.argv) == 1:
        print("Usage: python wpilib_scanner.py wpilibj_path")
        exit(1)

    cls = None
    if len(sys.argv) == 3:
        cls = sys.argv[2]

    output = compare_folders(wpilib, get_wpilib_dirs(sys.argv[1]))
    text_list = list()
    for item in sorted(output["children"], key=lambda k: k["name"]):
        if cls is None or cls == item["name"]:
            text_list.extend(stringize_summary(item))
    print_list(text_list)

    print(
        "\n{} Errors, {} Ignored errors ".format(
            output["errors"], output["ignored_errors"]
        )
    )
