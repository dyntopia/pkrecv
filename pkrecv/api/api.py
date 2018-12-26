from flask import Flask
from flask_restful import Api

from .token import Token


def init_api(app: Flask) -> None:
    """
    Initialize the API endpoints.
    """
    api = Api(app)
    api.add_resource(Token, "/api/v1/token")
