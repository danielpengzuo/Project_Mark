from pprint import pformat


def peek_json(jso, list_limit=2):
    """
    """
    def _summarize_dict(dct):
        return {
            key : _summarize_json(val)
            for key, val in dct.items()
        }

    def _summarize_list(lst):
        if len(lst) > list_limit:
            lst = lst[:2] + [ f'<{len(lst)} elements total...>' ]
        return [
            _summarize_json(element)
            for element in lst
        ]

    def _summarize_json(jso):
        if   isinstance(jso, dict):
            return _summarize_dict(jso)
        elif isinstance(jso, list):
            return _summarize_list(jso)
        else:
            # Leaves of JSON (string, numeric, or null)
            return jso

    summary = _summarize_json(jso)
    # TODO: return just the summary and let the client pprint?
    return pformat(summary)
