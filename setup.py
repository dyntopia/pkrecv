#!/usr/bin/env python3

import re
import sys
from typing import Iterator

import setuptools

import pkrecv


def get_requirements(filename: str) -> Iterator[str]:
    with open(filename, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith("#"):
                m = re.match(r"([a-zA-Z0-9-_]+)[ \t]*==[ \t]*([0-9\.]+)", line)
                if not m:
                    sys.exit("ERROR: invalid requirements.txt")
                yield "{0} >= {1}".format(*m.groups())


setuptools.setup(
    name="pkrecv",
    version=pkrecv.__version__,
    author="Hans Jerry Illikainen",
    author_email="hji@dyntopia.com",
    license="BSD-2-Clause",
    python_requires=">=3.5",
    install_requires=list(get_requirements("requirements/requirements.txt")),
    packages=["pkrecv"],
    entry_points={"console_scripts": ["pkrecv = pkrecv.__main__:main"]}
)
