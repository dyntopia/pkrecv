import tempfile
from unittest import TestCase

from munch import Munch

from pkrecv.config import Config, ConfigError


class ConfigReadTest(TestCase):
    def test_filename_list(self) -> None:
        cfg = Config()

        with tempfile.NamedTemporaryFile() as tmp1:
            tmp1.write(b"[flask]\n")
            tmp1.write(b"a = 1\n")
            tmp1.flush()
            with tempfile.NamedTemporaryFile() as tmp2:
                tmp2.write(b"[gunicorn]\n")
                tmp2.write(b"b = 2\n")
                tmp2.flush()
                cfg.read([tmp1.name, tmp2.name])

        flask = cfg.get_section("flask", Munch())
        gunicorn = cfg.get_section("gunicorn", Munch())

        self.assertEqual(flask.a, 1)
        self.assertEqual(gunicorn.b, 2)

    def test_filename_str(self) -> None:
        cfg = Config()

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"[flask]\n")
            tmp.write(b"a = True\n")
            tmp.flush()
            cfg.read(tmp.name)

        flask = cfg.get_section("flask", Munch())
        self.assertEqual(flask.a, True)

    def test_invalid_syntax(self) -> None:
        cfg = Config()

        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"...")
            tmp.flush()
            with self.assertRaises(ConfigError):
                cfg.read(tmp.name)


class ConfigGetSectionTest(TestCase):
    def setUp(self) -> None:
        self.cfg = Config()
        self.tmp = tempfile.NamedTemporaryFile()
        self.tmp.write(b"[asdf]\n")

    def tearDown(self) -> None:
        self.tmp.close()

    def test_default(self) -> None:
        default = {"x": "y"}
        xyz = self.cfg.get_section("xyz", default)
        self.assertIs(xyz, default)

    def test_bool(self) -> None:
        self.tmp.write(b"a = true\n")
        self.tmp.write(b"b = FAlse\n")
        self.tmp.write(b"c = yEs\n")
        self.tmp.write(b"d = no\n")
        self.tmp.flush()

        self.cfg.read(self.tmp.name)
        asdf = self.cfg.get_section("asdf", Munch())

        self.assertIsInstance(asdf.a, bool)
        self.assertIsInstance(asdf.b, bool)
        self.assertIsInstance(asdf.c, bool)
        self.assertIsInstance(asdf.d, bool)
        self.assertEqual(asdf.a, True)
        self.assertEqual(asdf.b, False)
        self.assertEqual(asdf.c, True)
        self.assertEqual(asdf.d, False)

    def test_int(self) -> None:
        self.tmp.write(b"a = 0\n")
        self.tmp.write(b"b = 1\n")
        self.tmp.write(b"c = 345\n")
        self.tmp.flush()

        self.cfg.read(self.tmp.name)
        asdf = self.cfg.get_section("asdf", Munch())

        self.assertIsInstance(asdf.a, int)
        self.assertIsInstance(asdf.b, int)
        self.assertIsInstance(asdf.c, int)
        self.assertEqual(asdf.a, 0)
        self.assertEqual(asdf.b, 1)
        self.assertEqual(asdf.c, 345)

    def test_float(self) -> None:
        self.tmp.write(b"a = 1.0\n")
        self.tmp.write(b"b = 2.3\n")
        self.tmp.write(b"c = 34.5\n")
        self.tmp.flush()

        self.cfg.read(self.tmp.name)
        asdf = self.cfg.get_section("asdf", Munch())

        self.assertIsInstance(asdf.a, float)
        self.assertIsInstance(asdf.b, float)
        self.assertIsInstance(asdf.c, float)
        self.assertEqual(asdf.a, 1.0)
        self.assertEqual(asdf.b, 2.3)
        self.assertEqual(asdf.c, 34.5)

    def test_str(self) -> None:
        self.tmp.write(b"a = heh\n")
        self.tmp.write(b"b = 1-2-3\n")
        self.tmp.flush()

        self.cfg.read(self.tmp.name)
        asdf = self.cfg.get_section("asdf", Munch())

        self.assertIsInstance(asdf.a, str)
        self.assertIsInstance(asdf.b, str)
        self.assertEqual(asdf.a, "heh")
        self.assertEqual(asdf.b, "1-2-3")
