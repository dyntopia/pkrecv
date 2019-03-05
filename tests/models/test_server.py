from unittest import TestCase

from pkrecv.models.server import (
    ServerError,
    add_server,
    get_servers,
    split_key
)
from pkrecv.models.token import add_token

from ..helpers import FlaskTestCase


class AddServerTest(FlaskTestCase):
    def test_invalid_key(self) -> None:
        with self.assertRaises(ServerError):
            add_server("ip", 1234, "", 1)

    def test_invalid_key_type_ssh_rsa1(self) -> None:
        with self.assertRaises(ServerError):
            add_server("ip", 1234, "ssh-rsa1 data comment", 1)

    def test_invalid_key_type_sh_rsa(self) -> None:
        with self.assertRaises(ServerError):
            add_server("ip", 1234, "sh-rsa data comment", 1)

    def test_invalid_key_data(self) -> None:
        with self.assertRaises(ServerError):
            add_server("ip", 1234, "ssh-ed25519 abc comment", 1)

    def test_success(self) -> None:
        add_token("server", "desc")
        add_server("ip", 1234, "ssh-rsa data comment", 1)

        servers = get_servers()
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip")
        self.assertEqual(servers[0].port, 1234)
        self.assertEqual(servers[0].key_type, "ssh-rsa")
        self.assertEqual(servers[0].key_data, "data")
        self.assertEqual(servers[0].key_comment, "comment")
        self.assertEqual(servers[0].token_id, 1)

    def test_strip_key(self) -> None:
        add_token("server", "desc")
        add_server("ip", 1234, "   ssh-rsa    data     comment    \n\n\n", 1)

        servers = get_servers()
        self.assertEqual(servers[0].key_type, "ssh-rsa")
        self.assertEqual(servers[0].key_data, "data")
        self.assertEqual(servers[0].key_comment, "comment")


class GetServersTest(FlaskTestCase):
    def test_id(self) -> None:
        add_token("server", "desc")
        add_server("ip1", 1111, "ssh-rsa data comment", 1)
        add_server("ip2", 2222, "ssh-ed25519 data comment", 1)

        servers = get_servers(id=2)
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip2")

    def test_ip(self) -> None:
        add_token("server", "desc")
        add_server("ip1", 1111, "ssh-rsa data comment", 1)
        add_server("ip2", 2222, "ssh-ed25519 data comment", 1)

        servers = get_servers(ip="ip1")
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].ip, "ip1")

    def test_all(self) -> None:
        add_token("server", "desc")

        for i in range(10):
            add_server("ip", i, "ssh-rsa data comment", 1)

        servers = get_servers()
        self.assertEqual(len(servers), 10)


class SplitKeyTest(TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ServerError):
            split_key("")

    def test_missing_data_and_comment(self) -> None:
        with self.assertRaises(ServerError):
            split_key("type")

    def test_excessive_fields(self) -> None:
        with self.assertRaises(ServerError):
            split_key("type data comment xyz")

    def test_missing_comment(self) -> None:
        self.assertEqual(split_key("type   data  "), ["type", "data", ""])

    def test_have_all_fields(self) -> None:
        self.assertEqual(split_key("type data cmt"), ["type", "data", "cmt"])
