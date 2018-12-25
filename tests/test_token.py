import hashlib
import re
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pkrecv.token import Token, TokenError, add_token, generate_token

from .helpers import FlaskTestCase


class AddTokenTest(FlaskTestCase):
    @patch("pkrecv.token.generate_token")  # type: ignore
    def test_sha256(self, mock: MagicMock) -> None:
        data = b"abcd"
        sha256 = hashlib.sha256(data).hexdigest()

        mock.return_value = data
        add_token("admin", "")

        tokens = Token.query.filter_by(token=sha256).all()
        self.assertEqual(len(tokens), 1)

    def test_invalid_role(self) -> None:
        with self.assertRaises(TokenError):
            add_token("abcd", "")


class GenerateTokenTest(TestCase):
    def test_length(self) -> None:
        self.assertEqual(len(generate_token(5)), 10)
        self.assertEqual(len(generate_token(32)), 64)

    def test_hex(self) -> None:
        token = generate_token(32).decode("ascii")
        self.assertIsNone(re.search("[^a-f0-9]", token))
