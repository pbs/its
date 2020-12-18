import base64
from functools import wraps

from flask import Response, abort, request

from its.settings import NAMESPACES


def check_token(namespace, authorization_header):
    key = NAMESPACES[namespace].get('key')
    secret = NAMESPACES[namespace].get('secret')
    token = base64.b64encode(
        (key + ":" + secret).encode("ascii")).decode("ascii")
    client_token = authorization_header.split()[-1]
    if client_token == token:
        return True


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        namespace = kwargs.get('namespace')
        if namespace not in NAMESPACES:
            abort(401, f"Invalid namespace.")
        if not authorization_header:
            abort(401, "Authentication credentials were not provided.")
        elif not check_token(namespace, authorization_header):
            abort(401, "Invalid authentication credentials.")
        return f(*args, **kwargs)
    return decorated
