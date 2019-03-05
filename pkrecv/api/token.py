from typing import Dict, Tuple, Union

from flask_restful import Resource, reqparse

from ..models.token import TokenError, add_token, delete_token, get_tokens
from .auth import login_required, role_required


class Token(Resource):  # type: ignore
    @staticmethod
    @login_required
    @role_required("admin")
    def get() -> Dict:
        """
        Retrieve a list of token IDs, roles and descriptions.
        """
        return {"tokens": get_tokens()}

    @staticmethod
    @login_required
    @role_required("admin")
    def post() -> Union[Dict, Tuple]:
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
            return {"message": str(e)}, 400
        return {"token": token}

    @staticmethod
    @login_required
    @role_required("admin")
    def delete() -> Union[Dict, Tuple]:
        """
        Delete a token.
        """
        p = reqparse.RequestParser()
        p.add_argument("id", type=int, required=True)
        args = p.parse_args()

        try:
            delete_token(args.id)
        except TokenError as e:
            return {"message": str(e)}, 400
        return {"message": "deleted"}
