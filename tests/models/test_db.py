from unittest import TestCase

from flask import Flask

from pkrecv.models.db import DBError, init_db


class InitDBTest(TestCase):
    def test_invalid_db(self) -> None:
        app = Flask(__name__)
        app.app_context().push()
        app.config["SQLALCHEMY_DATABASE_URI"] = "..."
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with self.assertRaises(DBError):
            init_db(app)
