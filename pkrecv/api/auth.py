import functools
import json
from typing import Any, Callable, Dict, Union

from flask import Response, g
from flask_httpauth import HTTPTokenAuth

from ..models.token import get_tokens

auth = HTTPTokenAuth()
login_required = auth.login_required


def role_required(*roles: str) -> Callable:
    """
    Authorize a token.
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Dict, Response]:
            token = g.get("token")
            if token and token.role in roles:
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
    t = get_tokens(token=token)
    if len(t) == 1:
        g.token = t[0]
        return True
    return False
