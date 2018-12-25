import os

from flask import Flask

from .db import db


class AppError(Exception):
    pass


def init_app(config: str) -> Flask:
    """
    Initialize flask and the database.
    """
    app = Flask(__name__)
    app.app_context().push()
    try:
        app.config.from_pyfile(os.path.expanduser(config))
    except (FileNotFoundError, SyntaxError) as e:
        raise AppError(e)

    db.init_app(app)
    db.create_all()

    return app
