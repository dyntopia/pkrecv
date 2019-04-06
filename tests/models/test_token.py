import re
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pkrecv.models.token import (
    Token,
    TokenError,
    add_token,
    delete_token,
    generate_token,
    get_tokens,
    sha256,
)

from ..helpers import FlaskTestCase


class AddTokenTest(FlaskTestCase):
    @patch("pkrecv.models.token.generate_token")
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


class DeleteTokenTest(FlaskTestCase):
    def test_invalid_id(self) -> None:
        with self.assertRaises(TokenError):
            delete_token(0)

        add_token("admin", "desc")

        with self.assertRaises(TokenError):
            delete_token(0)

    def test_success(self) -> None:
        add_token("admin", "desc0")
        add_token("server", "desc1")
        add_token("none", "desc2")

        delete_token(2)

        tokens = get_tokens()
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].role, "admin")
        self.assertEqual(tokens[1].role, "none")


class GetTokensTest(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.first = add_token("admin", "desc1")
        self.second = add_token("server", "desc2")
        self.third = add_token("none", "desc3")

    def test_excluded_field(self) -> None:
        tokens = get_tokens()
        self.assertEqual(len(tokens), 3)
        self.assertFalse("token" in tokens[0].keys())
        self.assertFalse("token" in tokens[1].keys())
        self.assertFalse("token" in tokens[2].keys())

    def test_id(self) -> None:
        first = get_tokens(id=1)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].id, 1)
        self.assertEqual(first[0].role, "admin")
        self.assertEqual(first[0].description, "desc1")

        second = get_tokens(id=2)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].id, 2)
        self.assertEqual(second[0].role, "server")
        self.assertEqual(second[0].description, "desc2")

        third = get_tokens(id=3)
        self.assertEqual(len(third), 1)
        self.assertEqual(third[0].id, 3)
        self.assertEqual(third[0].role, "none")
        self.assertEqual(third[0].description, "desc3")

    def test_token(self) -> None:
        first = get_tokens(token=self.first)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0].id, 1)
        self.assertEqual(first[0].role, "admin")
        self.assertEqual(first[0].description, "desc1")

        second = get_tokens(token=self.second)
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0].id, 2)
        self.assertEqual(second[0].role, "server")
        self.assertEqual(second[0].description, "desc2")

        third = get_tokens(token=self.third)
        self.assertEqual(len(third), 1)
        self.assertEqual(third[0].id, 3)
        self.assertEqual(third[0].role, "none")
        self.assertEqual(third[0].description, "desc3")

    def test_len(self) -> None:
        self.assertEqual(len(get_tokens()), 3)

        for _ in range(10):
            add_token("admin", "asdf")

        self.assertEqual(len(get_tokens()), 13)


class GenerateTokenTest(TestCase):
    def test_length(self) -> None:
        self.assertEqual(len(generate_token(5)), 10)
        self.assertEqual(len(generate_token(32)), 64)

    def test_hex(self) -> None:
        token = generate_token(32).decode("ascii")
        self.assertIsNone(re.search("[^a-f0-9]", token))
