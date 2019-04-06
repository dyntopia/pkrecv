from typing import Any, Dict

from flask import Flask

from .api.api import init_api
from .models.db import DBError, init_db


class AppError(Exception):
    pass


def init_app(options: Dict[str, Any]) -> Flask:
    """
    Initialize flask.
    """
    opts = {k.upper(): v for k, v in options.items()}
    app = Flask(__name__)
    app.app_context().push()  # type: ignore
    app.config.from_mapping(opts)  # type: ignore

    init_api(app)

    try:
        init_db(app)
    except DBError as e:
        raise AppError(e)

    return app
