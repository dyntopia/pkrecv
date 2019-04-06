import json

from pkrecv.models.server import add_server, get_servers
from pkrecv.models.token import add_token

from ..helpers import FlaskTestCase


class ServerGetTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.get("/api/v1/server")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_server(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }
        res = self.client.get("/api/v1/server", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_none(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("none", "desc")),
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
        self.assertEqual(servers[0]["key_type"], "ssh-rsa")
        self.assertEqual(servers[0]["key_data"], "...")
        self.assertEqual(servers[0]["key_comment"], "")

        self.assertEqual(servers[1]["id"], 2)
        self.assertEqual(servers[1]["ip"], "2")
        self.assertEqual(servers[1]["port"], 2)
        self.assertEqual(servers[1]["key_type"], "ssh-ed25519")
        self.assertEqual(servers[1]["key_data"], "...")
        self.assertEqual(servers[1]["key_comment"], "")

    def test_id_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "id": "2",
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ... c", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ... c", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 2)
        self.assertEqual(servers[0]["ip"], "2")
        self.assertEqual(servers[0]["port"], 2)
        self.assertEqual(servers[0]["key_type"], "ssh-ed25519")
        self.assertEqual(servers[0]["key_data"], "...")
        self.assertEqual(servers[0]["key_comment"], "c")

    def test_ip_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "ip": "2",
        }

        add_server(ip="1", port=1, public_key="ssh-rsa ... x", token_id=1)
        add_server(ip="2", port=2, public_key="ssh-ed25519 ... y", token_id=1)

        res = self.client.get("/api/v1/server", headers=headers, data=filters)
        data = json.loads(res.data.decode("utf-8"))
        servers = data["servers"]

        self.assertEqual(len(servers), 1)

        self.assertEqual(servers[0]["id"], 2)
        self.assertEqual(servers[0]["ip"], "2")
        self.assertEqual(servers[0]["port"], 2)
        self.assertEqual(servers[0]["key_type"], "ssh-ed25519")
        self.assertEqual(servers[0]["key_data"], "...")
        self.assertEqual(servers[0]["key_comment"], "y")

    def test_key_type_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "key_type": "ssh-ed25519",
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
        self.assertEqual(servers[0]["key_type"], "ssh-ed25519")
        self.assertEqual(servers[0]["key_data"], "...")
        self.assertEqual(servers[0]["key_comment"], "")

    def test_ip_and_key_type_filter(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc1")),
        }

        filters = {
            "ip": "3",
            "key_type": "ssh-ed25519",
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
        self.assertEqual(servers[0]["key_type"], "ssh-ed25519")
        self.assertEqual(servers[0]["key_data"], "...")
        self.assertEqual(servers[0]["key_comment"], "")


class ServerPostTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.post("/api/v1/server")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("none", "desc")),
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
            "public_key": "",
        }

        res = self.client.post("/api/v1/server", headers=headers, data=data)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "invalid public key")
        self.assertEqual(res.status_code, 400)

    def test_success_server(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }

        data = {
            "public_key": "ssh-rsa data comment",
        }

        res = self.client.post("/api/v1/server", headers=headers, data=data)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "added")
        self.assertEqual(res.status_code, 200)

        servers = get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].key_type, "ssh-rsa")
        self.assertEqual(servers[0].key_data, "data")
        self.assertEqual(servers[0].key_comment, "comment")

    def test_success_admin(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        data = {
            "public_key": "ecdsa-sha2-nistp384 data1234 comment321",
        }

        res = self.client.post("/api/v1/server", headers=headers, data=data)
        obj = json.loads(res.data.decode("utf-8"))
        self.assertEqual(obj["message"], "added")
        self.assertEqual(res.status_code, 200)

        servers = get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].key_type, "ecdsa-sha2-nistp384")
        self.assertEqual(servers[0].key_data, "data1234")
        self.assertEqual(servers[0].key_comment, "comment321")


class ServerDeleteTest(FlaskTestCase):
    def test_unauthenticated(self) -> None:
        res = self.client.delete("/api/v1/server")
        self.assertEqual(res.data, b"Unauthorized Access")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_none(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("none", "desc")),
        }

        data = {
            "id": 1,
        }

        add_server("10.0.0.1", 11, "ssh-rsa data", 1)

        res = self.client.delete("/api/v1/server", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_unauthorized_server(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("server", "desc")),
        }

        data = {
            "id": 1,
        }

        add_server("10.0.0.1", 11, "ssh-rsa data", 1)

        res = self.client.delete("/api/v1/server", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "Permission denied")
        self.assertEqual(res.status_code, 401)

    def test_missing_id(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        res = self.client.delete("/api/v1/server", headers=headers)
        data = json.loads(res.data.decode("utf-8"))
        self.assertTrue("Missing required parameter" in data["message"]["id"])
        self.assertEqual(res.status_code, 400)

    def test_invalid_id(self) -> None:
        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        data = {
            "id": 2,
        }

        add_server("10.0.0.1", 11, "ssh-rsa data", 1)

        res = self.client.delete("/api/v1/server", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "invalid server id 2")
        self.assertEqual(res.status_code, 400)

    def test_success(self) -> None:
        add_token("server", "desc")

        headers = {
            "Authorization": "Bearer {}".format(add_token("admin", "desc")),
        }

        data = {
            "id": 1,
        }

        add_server("10.0.0.1", 11, "ssh-rsa data", 1)
        add_server("10.0.0.2", 22, "ssh-rsa data", 1)
        add_server("10.0.0.2", 33, "ssh-rsa data", 1)

        res = self.client.delete("/api/v1/server", headers=headers, data=data)
        data = json.loads(res.data.decode("utf-8"))
        self.assertEqual(data["message"], "deleted")
        self.assertEqual(res.status_code, 200)

        res = self.client.get("/api/v1/server", headers=headers)
        servers = json.loads(res.data.decode("utf-8"))["servers"]
        self.assertEqual(len(servers), 2)
