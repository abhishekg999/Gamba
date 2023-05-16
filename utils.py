from flask import jsonify 

def jsonret(callback):
    """
    Flask safe wrapper to convert returned dictionaries to json

    Args:
        callback (function): Flask route handler
    """
    def inner(*args, **kwargs):
        return jsonify(callback(*args, **kwargs))

    inner.__name__ = callback.__name__
    return inner