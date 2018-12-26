import functools
import json
from typing import Any, Callable, Dict, Union

from flask import Response, g
from flask_httpauth import HTTPTokenAuth

from ..models.token import get_token

auth = HTTPTokenAuth()


def role_required(role: str) -> Callable:
    """
    Authorize a token.
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Dict, Response]:
            if g.get("role", None) == role:
                return f(*args, **kwargs)
            return Response(
                response=json.dumps({"message": "Permission denied"}),
                status=401,
                content_type="application/json"
            )
        return wrapper
    return decorator


@auth.verify_token
def verify_token(token: str) -> bool:
    """
    Authenticate a token.
    """
    t = get_token(token=token)
    if t:
        g.role = t.role
        return True
    return False
