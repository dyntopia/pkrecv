from flask import g
from flask_httpauth import HTTPTokenAuth

from ..models.token import get_token

auth = HTTPTokenAuth()


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
