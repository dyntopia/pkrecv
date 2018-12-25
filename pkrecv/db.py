import functools
import sqlite3

from typing import Any

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import _ConnectionRecord

db = SQLAlchemy()
column = functools.partial(Column, nullable=False)


@event.listens_for(Engine, "connect")
def set_sqlite3_pragma(dbapi_connection: Any, _: _ConnectionRecord) -> None:
    """
    Enforce foreign key constraints in SQLite3.

    Reference:
    https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()  # type: ignore
