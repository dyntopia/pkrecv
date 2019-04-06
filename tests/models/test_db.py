from unittest import TestCase

from flask import Flask

from pkrecv.models.db import DBError, Model, init_db


class InitDBTest(TestCase):
    def test_invalid_db(self) -> None:
        app = Flask(__name__)
        app.app_context().push()  # type: ignore
        app.config["SQLALCHEMY_DATABASE_URI"] = "..."
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        with self.assertRaises(DBError):
            init_db(app)


class ModelTest(TestCase):
    def test_invalid_type(self) -> None:
        with self.assertRaises(ValueError):
            Model._convert_value(None)  # pylint: disable=W0212
