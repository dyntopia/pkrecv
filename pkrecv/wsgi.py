from argparse import ArgumentParser
from typing import Dict, List

from flask import Flask
from gunicorn.app.base import BaseApplication


class Gunicorn(BaseApplication):  # type: ignore
    def __init__(self, app: Flask, options: Dict) -> None:
        self.app = app
        self.options = options
        super().__init__()

    def init(self, parser: ArgumentParser, opts: Dict, args: List) -> None:
        pass

    def load_config(self) -> None:
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Flask:
        return self.app
