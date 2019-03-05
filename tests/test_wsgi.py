from argparse import ArgumentParser
from unittest import TestCase

from pkrecv.wsgi import Gunicorn


class InitTest(TestCase):
    @staticmethod
    def test_implemented() -> None:
        gunicorn = Gunicorn(None, {})
        gunicorn.init(ArgumentParser(), {}, [])


class LoadConfigTest(TestCase):
    def test_lower(self) -> None:
        options = {
            "WORKERS": 99,
            "Bind": "127.0.0.1:1234"
        }
        gunicorn = Gunicorn(None, options)
        self.assertEqual(gunicorn.cfg.workers, 99)
        self.assertEqual(gunicorn.cfg.bind, ["127.0.0.1:1234"])


class TestLoad(TestCase):
    def test_app(self) -> None:
        app = ["app"]
        gunicorn = Gunicorn(app, {})
        self.assertIs(gunicorn.load(), app)
