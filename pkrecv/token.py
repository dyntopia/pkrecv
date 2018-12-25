import binascii
import datetime
import hashlib
import os
from typing import Any

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import validates

from .db import column, db


class TokenError(Exception):
    pass


class Token(db.Model):  # type: ignore
    roles = [
        "admin",
        "server"
    ]

    id = column(Integer, primary_key=True)
    token = column(String(128), unique=True)
    role = column(String(128))
    description = column(String(128), default="")
    created = column(DateTime, default=datetime.datetime.utcnow)

    @validates("role")
    def validate_role(self, _: str, role: str) -> str:
        if role not in self.roles:
            raise TokenError("{} is not a valid role".format(role))
        return role


def get_token(**filters: Any) -> Token:
    """
    Retrieve a token.
    """
    token = filters.get("token")
    if token:
        filters["token"] = sha256(bytes(token, "utf-8"))
    return Token.query.filter_by(**filters).first()


def add_token(role: str, description: str) -> str:
    """
    Add a token to the database.
    """
    token = generate_token(32)

    db.session.add(Token(
        token=sha256(token),
        role=role,
        description=description
    ))
    db.session.commit()

    return token.decode("ascii")


def generate_token(size: int) -> bytes:
    """
    Generate pseudorandom data and return its hexadecimal representation.
    """
    data = os.urandom(size)
    return binascii.hexlify(data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
