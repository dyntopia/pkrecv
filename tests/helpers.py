from unittest import TestCase

from pkrecv.app import init_app
from pkrecv.models.db import db


class FlaskTestCase(TestCase):
    def setUp(self) -> None:
        options = {
            "SQLALCHEMY_DATABASE_URI": "sqlite:///",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False
        }
        self.app = init_app(options)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
