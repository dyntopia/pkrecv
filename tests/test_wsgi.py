from unittest import TestCase

from pkrecv.wsgi import Gunicorn


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
