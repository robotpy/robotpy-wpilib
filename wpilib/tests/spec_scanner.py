import os
import sys
import plyj.parser
import plyj.model as m


plyj_parser = plyj.parser.Parser()


def scan_specifications(python_object, java_dir):
    outputs = list()
    for java_file in os.listdir(java_dir):
        name, ext = os.path.splitext(java_file)
        if ext != ".java":
            continue

        tree = plyj_parser.parse_file(os.path.join(java_dir, java_file))

        for type_decl in tree.type_declarations:
            if not hasattr(type_decl, "name"):
                continue
            result = {"name": type_decl.name}
            result["present"] = hasattr(python_object, type_decl.name)
            result["methods"] = list()
            result["correct"] = result["present"]
            if result["present"]:
                wpi_object = getattr(python_object, type_decl.name)
                for method_decl in [decl for decl in type_decl.body if type(decl) is m.MethodDeclaration]:
                    sub_result = dict()
                    sub_result["name"] = method_decl.name
                    sub_result["present"] = hasattr(wpi_object, method_decl.name)
                    result["methods"].append(sub_result)
                    if not sub_result["present"]:
                        result["correct"] = False
            outputs.append(result)
    return outputs


if __name__ == "__main__":
    import wpilib

    green_head = "\033[92m"
    red_head = "\033[91m"
    end_head = "\033[0m"
    dash_bar = "-----------------------"
    tab = "    "
    arrowtab = "--> "

    output = scan_specifications(wpilib, sys.argv[1])
    for item in output:

        print()
        print("".join([dash_bar, item["name"], dash_bar]))
        print()
        if item["correct"]:
            print("".join([green_head, "present and all correct!!", end_head]))
        elif not item["present"]:
            print("".join([red_head, "NOT present", end_head]))
        else:
            print("".join([red_head, "present, but NOT correct", end_head]))
            print()
            print("Displaying methods:")
            print()

            for method in item["methods"]:
                method_name = item["name"] + "." + method["name"] + "()"
                if method["present"]:
                    print("".join([green_head, tab, method_name, " present", end_head]))
                else:
                    print("".join([red_head, arrowtab, method_name, " NOT present", end_head]))