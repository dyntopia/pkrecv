import datetime
import functools
import sqlite3
from typing import Any, List, Optional, Union

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from munch import Munch
from sqlalchemy import Column, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import _ConnectionRecord

db = SQLAlchemy()
column = functools.partial(Column, nullable=False)


class DBError(Exception):
    pass


class Model(db.Model):  # type: ignore
    __abstract__ = True

    @property
    def as_dict(self) -> Munch:
        """
        Retrieve a row as a dict.
        """
        return self._to_dict()

    def _to_dict(self, exclude: Optional[List] = None) -> Munch:
        """
        Create a dict with all columns except for those in `exclude`.
        """
        if not exclude:
            exclude = []

        return Munch({
            c.key: self._convert_value(self.__dict__[c.key])
            for c in self.__table__.columns
            if c.key not in exclude
        })

    @staticmethod
    def _convert_value(value: Any) -> Union[bool, float, int, str]:
        """
        Convert a value to a serializable type.
        """
        if isinstance(value, (bool, float, int, str)):
            return value

        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")

        raise ValueError("unknown type for {}".format(value))


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
        cursor.close()


def init_db(app: Flask) -> None:
    """
    Initialize the database.
    """
    db.init_app(app)
    try:
        db.create_all()
    except SQLAlchemyError as e:
        raise DBError(e)
