
def match_arglist(args, kwargs, templates):
    """
    This compares args and kwargs against the argument templates in templates,
    :param args: The list of positional arguments
    :param kwargs: The list of keyword arguments
    :param templates: A list of dictionaries corresponding to possible
    argument list formats.

    An argument template is structured as follows:

    Each element in the list should be a tuple, corresponding to an argument name,
    and argument type condition. See types_match() for argument type condition structures.

    :returns The id of the selected template
    :returns A dictionary of argument name, value tuples.
    """

    #Try each template until we find one that works
    for template in templates:
        #List copies of the arguments
        arglist = list(reversed(args))
        kwarglist = [k for k in kwargs]
        results = dict()

        #Scan through all arguments and set valid to false if we find an issue.
        for arg_name, arg_type_condition in template:

            #Check kwargs first, then check args
            if arg_name in kwarglist:
                value = kwarglist.pop(arg_name)
            elif len(arglist) > 0:
                value = arglist.pop()
            else:
                value = None

            results[arg_name] = value

            #Check to see if identities match:
            if not types_match(value, arg_type_condition):
                break

        else:
            #If the results are valid and the argument lists are empty, return the results.
            if len(arglist) == 0 and len(kwarglist) == 0:
                return templates.index(template), results

    #We found nothing, then
    raise ValueError("Attribute error, attributes given did not match any argument templates.")

def types_match(object, type_structure):
    """
    :param object: the object to check
    :param type_structure: The structure, composed of lists, strings, and types,
    representing conditions that object must meet.

    Here are the possibilities for type_structure:
    - AttributeCondition
    - type_condition
    - list of type_structures
    - None

    If type_structure is an AttributeCondition, this will return False if
    any contained attribute is not present in object

    If type_structure is a type_condition, then object must be of the same type

    If type_structure is a list of type_structures, it is handled by running
    types_match on each item, and returning true if at least one matches.

    If type_structure is None, than everything matches it, and true is returned.
    """

    if type_structure is None:
        return True

    #Is it an attribute list?
    elif isinstance(type_structure, AttributeCondition):
        return type_structure.matches(object)

    elif isinstance(type_structure, list) and len(type_structure) != 0:
        #If the list is not an attribute condition, check each element
        #and return true if a match is found
        for type_condition in type_structure:
            if types_match(object, type_condition):
                return True
    else:
        return isinstance(object, type_structure)

class AttributeCondition:
    def __init__(self, *args):
        self.conditions = [arg for arg in args]

    def matches(self, object):
        for attribute in self.conditions:
            if not hasattr(object, attribute):
                return False
        else:
            return True