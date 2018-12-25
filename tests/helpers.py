import tempfile
from unittest import TestCase

from pkrecv.app import init_app
from pkrecv.db import db


class FlaskTestCase(TestCase):
    def setUp(self) -> None:
        self.config = tempfile.NamedTemporaryFile()
        self.config.write(b"SQLALCHEMY_DATABASE_URI = 'sqlite:///'\n")
        self.config.write(b"SQLALCHEMY_TRACK_MODIFICATIONS = False\n")
        self.config.flush()

        self.app = init_app(self.config.name)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.config.close()
