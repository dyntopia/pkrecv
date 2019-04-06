#!/usr/bin/env python3

import setuptools

import pkrecv

setuptools.setup(
    name="pkrecv",
    version=pkrecv.__version__,
    entry_points={"console_scripts": ["pkrecv = pkrecv.__main__:main"]}
)
