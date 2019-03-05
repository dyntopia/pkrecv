import json

from pkrecv.models.server import add_server, get_servers
from pkrecv.models.token import add_token

from ..helpers import FlaskTestCase


class ServerGetTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.get("/api/v1/server")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }
        res = self.client.get("/api/v1/server", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_no_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }
        add_server(ip="1", port=1, public_key="ssh-rsa ...", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ...", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 2)

        self.assertEqual(servers[0]["id"], 1)
        self.assertEqual(servers[0]["ip"], "1")
        self.assertEqual(servers[0]["port"], 1)
        self.assertEqual(servers[0]["key_type"], "rsa")
        self.assertEqual(servers[0]["key_data"], "ssh-rsa ...")

        self.assertEqual(servers[1]["id"], 2)
        self.assertEqual(servers[1]["ip"], "2")
        self.assertEqual(servers[1]["port"], 2)
        self.assertEqual(servers[1]["key_type"], "ed25519")
        self.assertEqual(servers[1]["key_data"], "ssh-ed25519 ...")

    def test_id_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "id": "2"
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ...", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ...", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 2)
        self.assertEqual(servers[0]["ip"], "2")
        self.assertEqual(servers[0]["port"], 2)
        self.assertEqual(servers[0]["key_type"], "ed25519")
        self.assertEqual(servers[0]["key_data"], "ssh-ed25519 ...")

    def test_ip_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "ip": "2"
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ...", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ...", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 2)
        self.assertEqual(servers[0]["ip"], "2")
        self.assertEqual(servers[0]["port"], 2)
        self.assertEqual(servers[0]["key_type"], "ed25519")
        self.assertEqual(servers[0]["key_data"], "ssh-ed25519 ...")

    def test_key_type_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "key_type": "ed25519"
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ...", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ...", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 2)
        self.assertEqual(servers[0]["ip"], "2")
        self.assertEqual(servers[0]["port"], 2)
        self.assertEqual(servers[0]["key_type"], "ed25519")
        self.assertEqual(servers[0]["key_data"], "ssh-ed25519 ...")

    def test_ip_and_key_type_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "ip": "3",
            "key_type": "ed25519"
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ...", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ...", token_id=1)
        add_server(ip="3", port=3, public_key="ssh-ed25519 ...", token_id=1)
        add_server(ip="4", port=4, public_key="ssh-ed25519 ...", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 3)
        self.assertEqual(servers[0]["ip"], "3")
        self.assertEqual(servers[0]["port"], 3)
        self.assertEqual(servers[0]["key_type"], "ed25519")
        self.assertEqual(servers[0]["key_data"], "ssh-ed25519 ...")


class ServerPostTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.post("/api/v1/server")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }
        res = self.client.post("/api/v1/server", headers=headers)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_missing_public_key(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }
        res = self.client.post("/api/v1/server", headers=headers)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertTrue("public_key" in obj["message"].keys())
        self.assertEqual(res.status_code, 400)

    def test_invalid_public_key(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }

        data = {
            "public_key": ""
        }

        res = self.client.post("/api/v1/server", headers=headers, data=data)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "could not determine key type")
        self.assertEqual(res.status_code, 400)

    def test_success(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }

        data = {
            "public_key": "ssh-rsa key comment"
        }

        res = self.client.post("/api/v1/server", headers=headers, data=data)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "added")
        self.assertEqual(res.status_code, 200)

        servers = get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].key_type, "rsa")
        self.assertEqual(servers[0].key_data, "ssh-rsa key comment")
