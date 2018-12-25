import hashlib
import re
from unittest import TestCase
from unittest.mock import MagicMock, patch

from flask import Flask

from pkrecv.db import db
from pkrecv.token import Token, add_token, generate_token


class AddTokenTest(TestCase):
    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.app_context().push()

        db.init_app(self.app)
        db.create_all()

    @patch("pkrecv.token.generate_token")  # type: ignore
    def test_sha256(self, mock: MagicMock) -> None:
        data = b"abcd"
        sha256 = hashlib.sha256(data).hexdigest()

        mock.return_value = data
        add_token("", "")

        tokens = Token.query.filter_by(token=sha256).all()
        self.assertEqual(len(tokens), 1)


class GenerateTokenTest(TestCase):
    def test_length(self) -> None:
        self.assertEqual(len(generate_token(5)), 10)
        self.assertEqual(len(generate_token(32)), 64)

    def test_hex(self) -> None:
        token = generate_token(32).decode("ascii")
        self.assertIsNone(re.search("[^a-f0-9]", token))
