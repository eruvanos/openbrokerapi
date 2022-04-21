from typing import Union, Iterable, Any


def _to_dict(obj):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = _to_dict(v)
        return data
    elif hasattr(obj, "__iter__") and not isinstance(obj, str):
        return [_to_dict(v) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict(
            [
                (key, _to_dict(value))
                for key, value in obj.__dict__.items()
                if not callable(value) and not key.startswith("_") and value is not None
            ]
        )
        return data
    else:
        return obj


def version_tuple(v):
    return tuple(map(int, (v.split("."))))


def ensure_list(x: Union[Iterable, Any]):
    import collections

    if isinstance(x, collections.abc.Iterable):
        return x
    else:
        return [x]


def to_json_response(obj):
    """Following https://stackoverflow.com/a/1118038"""
    from flask import jsonify

    return jsonify(_to_dict(obj))
