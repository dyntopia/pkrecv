from unittest import TestCase

from pkrecv.app import init_app


class InitAppTest(TestCase):
    def test_upper(self) -> None:
        options = {
            "sqlalchemy_database_URI": "sqlite:///",
            "sqlalchemy_track_modifications": False
        }
        app = init_app(options)

        self.assertEqual(app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///")
        self.assertEqual(app.config["SQLALCHEMY_TRACK_MODIFICATIONS"], False)
