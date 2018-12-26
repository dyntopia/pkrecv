import json
from typing import Dict, Union

from flask import Response
from flask_restful import Resource, reqparse

from ..models.token import TokenError, add_token, get_tokens
from .auth import login_required, role_required


class Token(Resource):  # type: ignore
    @staticmethod
    @login_required
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
    @login_required
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
