from typing import Any, Dict

from flask import Flask

from .api.api import init_api
from .models.db import init_db


class AppError(Exception):
    pass


def init_app(options: Dict[str, Any]) -> Flask:
    """
    Initialize flask.
    """
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_mapping({k.upper(): v for k, v in options.items()})

    init_api(app)
    init_db(app)

    return app
