import json
from typing import Dict, Union

from flask import Flask, Response, g
from flask_httpauth import HTTPTokenAuth
from flask_restful import Api, Resource, reqparse

from ..models.token import TokenError, add_token, get_token, get_tokens
from .rbac import role_required

auth = HTTPTokenAuth()


class Token(Resource):  # type: ignore
    @staticmethod
    @auth.login_required
    @role_required("admin")
    def get() -> Union[Dict, Response]:
        """
        Retrieve a list of token IDs, roles and descriptions.
        """
        return {
            "tokens": [
                {"id": t.id, "role": t.role, "description": t.description}
                for t in get_tokens()
            ]
        }

    @staticmethod
    @auth.login_required
    @role_required("admin")
    def post() -> Union[Dict, Response]:
        """
        Create a new token.
        """
        p = reqparse.RequestParser()
        p.add_argument("role", type=str, required=True)
        p.add_argument("description", type=str)
        args = p.parse_args()

        try:
            token = add_token(args.role, args.description)
        except TokenError as e:
            return Response(
                response=json.dumps({"message": str(e)}),
                status=400,
                content_type="application/json"
            )
        return {"token": token}


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


def init_api(app: Flask) -> None:
    """
    Initialize the API endpoints.
    """
    api = Api(app)
    api.add_resource(Token, "/api/v1/token")
