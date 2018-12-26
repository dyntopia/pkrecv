import re
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pkrecv.models.token import (
    Token,
    TokenError,
    add_token,
    generate_token,
    get_tokens,
    sha256
)

from ..helpers import FlaskTestCase


class AddTokenTest(FlaskTestCase):
    @patch("pkrecv.models.token.generate_token")  # type: ignore
    def test_sha256(self, mock: MagicMock) -> None:
        data = b"abcd"
        sha256sum = sha256(data)

        mock.return_value = data
        add_token("admin", "")

        tokens = Token.query.filter_by(token=sha256sum).all()
        self.assertEqual(len(tokens), 1)

    def test_invalid_role(self) -> None:
        with self.assertRaises(TokenError):
            add_token("abcd", "")


class GetTokensTest(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.first = add_token("admin", "desc1")
        self.second = add_token("server", "desc2")

    def test_id(self) -> None:
        first = get_tokens(id=1)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].id, 1)
        self.assertEqual(first[0].token, sha256(bytes(self.first, "ascii")))
        self.assertEqual(first[0].role, "admin")
        self.assertEqual(first[0].description, "desc1")

        second = get_tokens(id=2)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].id, 2)
        self.assertEqual(second[0].token, sha256(bytes(self.second, "ascii")))
        self.assertEqual(second[0].role, "server")
        self.assertEqual(second[0].description, "desc2")

    def test_token(self) -> None:
        first = get_tokens(token=self.first)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].id, 1)
        self.assertEqual(first[0].token, sha256(bytes(self.first, "ascii")))
        self.assertEqual(first[0].role, "admin")
        self.assertEqual(first[0].description, "desc1")

        second = get_tokens(token=self.second)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].id, 2)
        self.assertEqual(second[0].token, sha256(bytes(self.second, "ascii")))
        self.assertEqual(second[0].role, "server")
        self.assertEqual(second[0].description, "desc2")

    def test_len(self) -> None:
        self.assertEqual(len(get_tokens()), 2)

        for _ in range(10):
            add_token("admin", "asdf")

        self.assertEqual(len(get_tokens()), 12)


class GenerateTokenTest(TestCase):
    def test_length(self) -> None:
        self.assertEqual(len(generate_token(5)), 10)
        self.assertEqual(len(generate_token(32)), 64)

    def test_hex(self) -> None:
        token = generate_token(32).decode("ascii")
        self.assertIsNone(re.search("[^a-f0-9]", token))
