
def match_arglist(args, kwargs, templates):
    """
    This compares args and kwargs against the argument templates in templates,
    :param args: The list of positional arguments
    :param kwargs: The list of keyword arguments
    :param templates: A list of dictionaries corresponding to possible
    argument list formats.

    An argument list is basically a list of argument name, type tuples.

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
        for arg_name, arg_identity in template:
            #Check kwargs first, then check args
            if arg_name in kwarglist:
                value = kwarglist.pop(arg_name)
            elif len(arglist) > 0:
                value = arglist.pop()
            else:
                value = None

            results[arg_name] = value

            #Check to see if identities match:

            if arg_identity is not None:

                if isinstance(arg_identity, str) and len(arg_identity) != 0:
                    if not hasattr(value, arg_identity):
                        break
                elif isinstance(arg_identity, list) and len(arg_identity) != 0:
                    correct = True
                    for arg in arg_identity:
                        if isinstance(arg, str):
                            if not hasattr(value, arg):
                                correct = False
                                break
                        else:
                            if isinstance(value, arg):
                                correct = True

                    if not correct:
                        break

                elif not isinstance(value, arg_identity):
                        break
        else:
            #If the results are valid and the argument lists are empty, return the results.
            if len(arglist) == 0 and len(kwarglist) == 0:
                return templates.index(template), results

    #We found nothing, then
    raise ValueError("Attribute error, attributes given did not match any argument templates.")
