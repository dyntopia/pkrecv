import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from pkrecv import app, cli, config
from pkrecv.models import token


class CliTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.config = tempfile.NamedTemporaryFile()

    def tearDown(self) -> None:
        self.config.close()

    @patch("pkrecv.config.Config.read")
    def test_config_error(self, mock: MagicMock) -> None:
        mock.side_effect = config.ConfigError("asdf")

        args = [
            "--config-file",
            self.config.name,
            "add-token",
        ]
        runner = CliRunner()
        result = runner.invoke(cli.cli, args)
        self.assertEqual(result.output, "ERROR: asdf\n")
        self.assertEqual(result.exit_code, 1)

    @patch("pkrecv.app.init_app")
    def test_app_error(self, mock: MagicMock) -> None:
        mock.side_effect = app.AppError("xyz")

        args = [
            "--config-file",
            self.config.name,
            "add-token",
        ]
        runner = CliRunner()
        result = runner.invoke(cli.cli, args)
        self.assertEqual(result.output, "ERROR: xyz\n")
        self.assertEqual(result.exit_code, 1)


class AddTokenTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.config = tempfile.NamedTemporaryFile()
        self.config.write(
            b"""
            [flask]
            sqlalchemy_database_uri = sqlite:///:memory:
            sqlalchemy_track_modifications = false
            """
        )
        self.config.flush()

    def tearDown(self) -> None:
        self.config.close()

    @patch("pkrecv.models.token.add_token")
    def test_token_error(self, mock: MagicMock) -> None:
        mock.side_effect = token.TokenError("xyz")

        args = [
            "--config-file",
            self.config.name,
            "add-token",
            "--role",
            "admin",
        ]
        runner = CliRunner()
        result = runner.invoke(cli.cli, args)
        self.assertEqual(result.output, "ERROR: xyz\n")
        self.assertEqual(result.exit_code, 1)

    @patch("pkrecv.models.token.add_token")
    def test_token_success(self, mock: MagicMock) -> None:
        mock.return_value = "abcd"

        args = [
            "--config-file",
            self.config.name,
            "add-token",
            "--role",
            "admin",
        ]
        runner = CliRunner()
        result = runner.invoke(cli.cli, args)
        self.assertEqual(result.output, "Token: abcd\n")
        self.assertEqual(result.exit_code, 0)


class ServeTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.config = tempfile.NamedTemporaryFile()
        self.config.write(
            b"""
            [flask]
            sqlalchemy_database_uri = sqlite:///:memory:
            sqlalchemy_track_modifications = false
            """
        )
        self.config.flush()

    def tearDown(self) -> None:
        self.config.close()

    @patch("pkrecv.wsgi.Gunicorn.run")
    def test_serve(self, mock: MagicMock) -> None:
        args = [
            "--config-file",
            self.config.name,
            "serve",
        ]
        runner = CliRunner()
        result = runner.invoke(cli.cli, args)

        self.assertEqual(len(mock.mock_calls), 1)
        self.assertEqual(result.exit_code, 0)
