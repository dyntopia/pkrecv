from typing import Dict

from flask_restful import Resource, reqparse

from ..models.server import get_servers
from .auth import login_required, role_required


class Server(Resource):  # type: ignore
    @staticmethod
    @login_required
    @role_required("admin")
    def get() -> Dict:
        """
        Retrieve a list of servers.
        """
        p = reqparse.RequestParser()
        p.add_argument("ip", type=str)
        p.add_argument("key_type", type=str)
        args = p.parse_args()

        servers = get_servers(**{key: args[key] for key in args if args[key]})
        return {"servers": servers}
