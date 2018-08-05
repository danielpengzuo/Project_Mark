import ast
import json


def parse(raw_str):
    """
    Parse json strings that are not really json...

    Some terribly-written server returns JSONs with single quotes,
    which the `json` module cannot handle.  We make several attempts
    in order.  See comments below.
    """
    try:
        # The compliant case, good
        return json.loads(raw_str)
    except:
        pass

    try:
        # Handles single quotes...
        return ast.literal_eval(raw_str)
    except ValueError:
        # ...but not null
        pass

    # Last attempt: replace all single quotes with double quotes
    # and try `json.loads` again.  This runs the risk of changing
    # the quotation literals in a returned string.
    return json.loads(raw_str.replace("'", '"'))


