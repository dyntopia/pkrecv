import json

from pkrecv.token import add_token

from .helpers import FlaskTestCase


class TokenGetTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.get("/api/v1/token")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }
        res = self.client.get("/api/v1/token", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_success(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }
        add_token("server", "desc2")
        add_token("admin", "desc3")

        res = self.client.get("/api/v1/token", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        tokens = data["tokens"]

        self.assertEqual(len(tokens), 3)

        self.assertEqual(tokens[0]["id"], 1)
        self.assertEqual(tokens[0]["role"], "admin")
        self.assertEqual(tokens[0]["description"], "desc1")

        self.assertEqual(tokens[1]["id"], 2)
        self.assertEqual(tokens[1]["role"], "server")
        self.assertEqual(tokens[1]["description"], "desc2")

        self.assertEqual(tokens[2]["id"], 3)
        self.assertEqual(tokens[2]["role"], "admin")
        self.assertEqual(tokens[2]["description"], "desc3")


class TokenPostTest(FlaskTestCase):
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
