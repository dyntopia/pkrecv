from typing import Dict, Tuple, Union

from flask_restful import Resource, reqparse

from ..models.token import TokenError, add_token, get_tokens
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
