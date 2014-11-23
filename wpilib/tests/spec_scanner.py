import os
import sys
import plyj.parser
import plyj.model as m
import inspect


plyj_parser = plyj.parser.Parser()

green_head = "\033[92m"
red_head = "\033[91m"
end_head = "\033[0m"
dash_bar = "-----------------------"
class_start = dash_bar + "{}" + dash_bar
class_end = dash_bar + "End Class {}" + dash_bar
tab = "    "
arrowtab = "--> "


def scan_specifications(python_object, java_dirs):
    outputs = list()
    java_files = list()
    for dir in java_dirs:
        java_files.extend([os.path.join(dir, s) for s in os.listdir(dir)])
    for java_file in java_files:
        name, ext = os.path.splitext(os.path.basename(java_file))
        if ext != ".java":
            continue

        tree = plyj_parser.parse_file(java_file)

        for java_child in tree.type_declarations:
            if not isinstance(java_child, m.ClassDeclaration) and not isinstance(java_child, m.MethodDeclaration):
                continue
            python_child = None
            if hasattr(python_object, java_child.name):
                python_child = getattr(python_object, java_child.name)

            outputs.append(compare_object(python_child, java_child))
    return outputs


def compare_object(python_object, java_object):
    output = dict()
    output["name"] = java_object.name
    output["present"] = python_object is not None
    output["matches"] = output["present"]
    output["type"] = java_object.__class__.__name__
    if output["type"] == "MethodDeclaration":
        output["parameters"] = list()
        for p in java_object.parameters:
            if isinstance(p.type, str):
                output["parameters"].append({"type": p.type, "name": p.variable.name})
            elif isinstance(p.type.name, str):
                output["parameters"].append({"type": p.type.name, "name": p.variable.name})
            else:
                output["parameters"].append({"type": p.type.name.value, "name": p.variable.name})
        if output["present"]:
            args, varargs, keywords, defaults = inspect.getargspec(python_object)
            if varargs is None and keywords is None:
                args = [a for a in args if a != "self"]
                if len(args) < len(output["parameters"]):
                    output["matches"] = False

    elif output["type"] == "ClassDeclaration":
        output["children"] = list()
        for java_child in java_object.body:
            if not isinstance(java_child, m.ClassDeclaration) and not isinstance(java_child, m.MethodDeclaration):
                continue
            python_child = None
            if hasattr(python_object, java_child.name):
                python_child = getattr(python_object, java_child.name)
            else:
                output["matches"] = False
            output["children"].append(compare_object(python_child, java_child))
    return output


def stringize_summary(summary):
    output = list()
    if summary["type"] == "ClassDeclaration":
        output.append({"text": "", "color": ""})
        output.append({"text": class_start.format(summary["name"]), "color": ""})
        present_msg = "is present"
        color = "green"
        if not summary["present"]:
            present_msg = "is NOT present"
            color = "red"
        matches_msg = "does match"
        if not summary["matches"]:
            matches_msg = "does NOT match"
            color = "red"
        output.append({"text": "".join([present_msg, ", ", matches_msg]), "color": color})
        if not summary["matches"]:
            methods = [cl for cl in summary["children"] if cl["type"] == "MethodDeclaration"]
            if len(methods) != 0:
                output.append({"text": "", "color": ""})
                output.append({"text": "Methods:", "color": ""})
                output.append({"text": "", "color": ""})
                for f in methods:
                    for t in stringize_summary(f):
                        if t["color"] == "red":
                            t["text"] = arrowtab + t["text"]
                        else:
                            t["text"] = tab + t["text"]
                        output.append(t)
                output.append({"text": "", "color": ""})
            subclasses = [cl for cl in summary["children"] if cl["type"] != "MethodDeclaration"]
            if len(subclasses) != 0:
                output.append({"text": "", "color": ""})
                output.append({"text": "Subclasses:", "color": ""})
                output.append({"text": "", "color": ""})
                for f in subclasses:
                    for t in stringize_summary(f):
                        t["text"] = tab + t["text"]
                        output.append(t)
                output.append({"text": "", "color": ""})
        #output.append({"text": class_end.format(summary["name"]), "color": ""})
        #output.append({"text": "", "color": ""})
    elif summary["type"] == "MethodDeclaration":
        present_msg = "is present"
        color = "green"
        if not summary["present"]:
            present_msg = "is NOT present"
            color = "red"
        matches_msg = "does match"
        if not summary["matches"]:
            matches_msg = "does NOT match"
            color = "red"
        text = summary["name"] + "(" + ", ".join(arg["type"] + " " + arg["name"] for arg in summary["parameters"]) + \
               ") " + present_msg + ", " + matches_msg
        output.append({"text": text, "color": color})
    return output


def print_list(inp):
    for text in inp:
        if text["color"] == "green":
            print(green_head + text["text"] + end_head)
        elif text["color"] == "red":
            print(red_head + text["text"] + end_head)
        else:
            print(text["text"])


if __name__ == "__main__":
    import wpilib

    output = scan_specifications(wpilib, sys.argv[1:])
    text_list = list()
    for item in output:
        text_list.extend(stringize_summary(item))
    print_list(text_list)
