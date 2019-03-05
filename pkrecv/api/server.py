from typing import Dict, Tuple, Union

from flask import g, request
from flask_restful import Resource, reqparse

from ..models.server import ServerError, add_server, get_servers
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
        p.add_argument("id", type=str)
        p.add_argument("ip", type=str)
        p.add_argument("key_type", type=str)
        args = p.parse_args()

        servers = get_servers(**{key: args[key] for key in args if args[key]})
        return {"servers": servers}

    @staticmethod
    @login_required
    @role_required("admin", "server")
    def post() -> Union[Dict, Tuple]:
        """
        Add a server.
        """
        p = reqparse.RequestParser()
        p.add_argument("public_key", type=str, required=True)
        args = p.parse_args()

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        try:
            add_server(ip, 22, args["public_key"], g.token.id)
        except ServerError as e:
            return {"message": str(e)}, 400
        return {"message": "added"}
