from unittest import TestCase

from pkrecv.models.server import (
    ServerError,
    add_server,
    get_key_type,
    get_servers
)
from pkrecv.models.token import add_token

from ..helpers import FlaskTestCase


class AddServerTest(FlaskTestCase):
    def test_invalid_key(self) -> None:
        with self.assertRaises(ServerError):
            add_server("ip", 1234, "", 1)

    def test_success(self) -> None:
        add_token("server", "desc")
        add_server("ip", 1234, "ssh-rsa key comment", 1)

        servers = get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip")
        self.assertEqual(servers[0].port, 1234)
        self.assertEqual(servers[0].key_type, "rsa")
        self.assertEqual(servers[0].public_key, "ssh-rsa key comment")
        self.assertEqual(servers[0].token_id, 1)


class GetServersTest(FlaskTestCase):
    def test_id(self) -> None:
        add_token("server", "desc")
        add_server("ip1", 1111, "ssh-rsa key comment", 1)
        add_server("ip2", 2222, "ssh-ed25519 key comment", 1)

        servers = get_servers(id=2)
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip2")

    def test_ip(self) -> None:
        add_token("server", "desc")
        add_server("ip1", 1111, "ssh-rsa key comment", 1)
        add_server("ip2", 2222, "ssh-ed25519 key comment", 1)

        servers = get_servers(ip="ip1")
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip1")

    def test_all(self) -> None:
        add_token("server", "desc")

        for i in range(10):
            add_server("ip", i, "ssh-rsa key comment", 1)

        servers = get_servers()
        self.assertEqual(len(servers), 10)


class GetKeyTypeTest(TestCase):
    def test_invalid(self) -> None:
        with self.assertRaises(ServerError):
            get_key_type("")

    def test_rsa(self) -> None:
        self.assertEqual(get_key_type("ssh-rsa key comment"), "rsa")

    def test_ed25519(self) -> None:
        self.assertEqual(get_key_type("ssh-ed25519 key comment"), "ed25519")
