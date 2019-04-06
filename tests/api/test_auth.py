from flask import Response, g

from pkrecv.api.auth import role_required, verify_token
from pkrecv.models.token import add_token

from ..helpers import FlaskTestCase


class VerifyTokenTest(FlaskTestCase):
    def test_no_tokens_none(self) -> None:
        self.assertFalse(verify_token(None))
        self.assertEqual(g.get("token"), None)

    def test_no_tokens_empty(self) -> None:
        self.assertFalse(verify_token(""))
        self.assertEqual(g.get("token"), None)

    def test_no_tokens_str(self) -> None:
        self.assertFalse(verify_token("abcd"))
        self.assertEqual(g.get("token"), None)

    def test_no_tokens_wildcard(self) -> None:
        self.assertFalse(verify_token("*"))
        self.assertEqual(g.get("token"), None)

    def test_none(self) -> None:
        add_token("admin", "desc1")
        add_token("server", "desc2")
        add_token("none", "desc3")

        self.assertFalse(verify_token(None))
        self.assertEqual(g.get("token"), None)

    def test_empty(self) -> None:
        add_token("admin", "desc1")
        add_token("server", "desc2")
        add_token("none", "desc3")

        self.assertFalse(verify_token(""))
        self.assertEqual(g.get("token"), None)

    def test_wildcard(self) -> None:
        add_token("admin", "desc1")
        add_token("server", "desc2")
        add_token("none", "desc3")

        self.assertFalse(verify_token("*"))
        self.assertEqual(g.get("token"), None)

    def test_invalid_token(self) -> None:
        first = add_token("admin", "desc1")
        second = add_token("server", "desc2")
        add_token("none", "desc3")

        invalid = first[:int(len(first) / 2)] + second[int(len(second) / 2):]
        self.assertFalse(verify_token(invalid))
        self.assertEqual(g.get("token"), None)

    def test_success_admin(self) -> None:
        token = add_token("admin", "admin1 desc")
        add_token("admin", "admin2 desc")
        add_token("server", "server1 desc")
        add_token("server", "server2 desc")
        add_token("none", "none1 desc")
        add_token("none", "none2 desc")

        self.assertTrue(verify_token(token))
        self.assertEqual(g.token.id, 1)
        self.assertEqual(g.token.role, "admin")
        self.assertEqual(g.token.description, "admin1 desc")

    def test_success_server(self) -> None:
        add_token("admin", "admin1 desc")
        add_token("admin", "admin2 desc")
        add_token("server", "server1 desc")
        token = add_token("server", "server2 desc")
        add_token("none", "none1 desc")
        add_token("none", "none2 desc")

        self.assertTrue(verify_token(token))
        self.assertEqual(g.token.id, 4)
        self.assertEqual(g.token.role, "server")
        self.assertEqual(g.token.description, "server2 desc")

    def test_success_none(self) -> None:
        add_token("admin", "admin1 desc")
        add_token("admin", "admin2 desc")
        add_token("server", "server1 desc")
        add_token("server", "server2 desc")
        token = add_token("none", "none1 desc")
        add_token("none", "none2 desc")

        self.assertTrue(verify_token(token))
        self.assertEqual(g.token.id, 5)
        self.assertEqual(g.token.role, "none")
        self.assertEqual(g.token.description, "none1 desc")


class RoleRequiredTest(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.admin0 = add_token("admin", "admin1 desc")
        self.admin1 = add_token("admin", "admin1 desc")
        self.server0 = add_token("server", "server1 desc")
        self.server1 = add_token("server", "server2 desc")
        self.none0 = add_token("none", "none1 desc")
        self.none1 = add_token("none", "none2 desc")

    def test_unauthenticated(self) -> None:
        self.assertEqual(self.require_admin().status_code, 401)
        self.assertEqual(self.require_admin_or_server().status_code, 401)
        self.assertEqual(self.require_server().status_code, 401)
        self.assertEqual(self.require_none().status_code, 401)
        self.assertEqual(self.require_none_or_server().status_code, 401)

    def test_admin(self) -> None:
        verify_token(self.admin0)

        self.assertEqual(self.require_admin().status_code, 200)
        self.assertEqual(self.require_admin_or_server().status_code, 200)
        self.assertEqual(self.require_server().status_code, 401)
        self.assertEqual(self.require_none().status_code, 401)
        self.assertEqual(self.require_none_or_server().status_code, 401)

    def test_server(self) -> None:
        verify_token(self.server1)

        self.assertEqual(self.require_admin().status_code, 401)
        self.assertEqual(self.require_admin_or_server().status_code, 200)
        self.assertEqual(self.require_server().status_code, 200)
        self.assertEqual(self.require_none().status_code, 401)
        self.assertEqual(self.require_none_or_server().status_code, 200)

    def test_none(self) -> None:
        verify_token(self.none0)

        self.assertEqual(self.require_admin().status_code, 401)
        self.assertEqual(self.require_admin_or_server().status_code, 401)
        self.assertEqual(self.require_server().status_code, 401)
        self.assertEqual(self.require_none().status_code, 200)
        self.assertEqual(self.require_none_or_server().status_code, 200)

    @staticmethod
    @role_required("admin")
    def require_admin() -> Response:
        return Response(status=200)

    @staticmethod
    @role_required("server")
    def require_server() -> Response:
        return Response(status=200)

    @staticmethod
    @role_required("none")
    def require_none() -> Response:
        return Response(status=200)

    @staticmethod
    @role_required("admin", "server")
    def require_admin_or_server() -> Response:
        return Response(status=200)

    @staticmethod
    @role_required("none", "server")
    def require_none_or_server() -> Response:
        return Response(status=200)
