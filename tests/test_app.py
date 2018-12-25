import tempfile
from unittest import TestCase

from pkrecv.app import AppError, init_app


class InitAppTest(TestCase):
    def test_file_not_found(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            pass

        with self.assertRaises(AppError):
            init_app(tmp.name)

    def test_syntax_error(self) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b".")
            tmp.flush()
            with self.assertRaises(AppError):
                init_app(tmp.name)
