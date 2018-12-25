import json
import tempfile
from unittest import TestCase

from pkrecv.app import init_app
from pkrecv.token import add_token


class TokenPostTest(TestCase):
    def setUp(self) -> None:
        self.config = tempfile.NamedTemporaryFile()
        self.config.write(b"SQLALCHEMY_DATABASE_URI = 'sqlite:///'\n")
        self.config.write(b"SQLALCHEMY_TRACK_MODIFICATIONS = False\n")
        self.config.flush()

        self.app = init_app(self.config.name)
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.config.close()

    def test_unauthenticated(self) -> None:
        res = self.client.post("/api/v1/token")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }
        res = self.client.post("/api/v1/token", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_missing_role(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }
        res = self.client.post("/api/v1/token", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertIsInstance(data["message"]["role"], str)
        self.assertEqual(res.status_code, 400)

    def test_invalid_role(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        data = {
            "role": "x"
        }

        res = self.client.post("/api/v1/token", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "x is not a valid role")
        self.assertEqual(res.status_code, 400)

    def test_success(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        data = {
            "role": "server"
        }

        res = self.client.post("/api/v1/token", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertIsInstance(data.get("token"), str)
        self.assertEqual(res.status_code, 200)
