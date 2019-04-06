import binascii
import datetime
import hashlib
import os
from typing import Any, List

from munch import Munch
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import validates

from .db import Model, column, db


class TokenError(Exception):
    pass


class Token(Model):
    roles = [
        "admin",
        "server",
        "none",
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

    @property
    def as_dict(self) -> Munch:
        return self._to_dict(["token"])


def get_tokens(**filters: Any) -> List[Token]:
    """
    Retrieve a list of tokens.
    """
    token = filters.get("token")
    if token:
        filters["token"] = sha256(bytes(token, "utf-8"))
    return [t.as_dict for t in Token.query.filter_by(**filters).all()]


def add_token(role: str, description: str) -> str:
    """
    Add a token to the database.
    """
    token = generate_token(32)

    db.session.add(
        Token(token=sha256(token), role=role, description=description)
    )
    db.session.commit()

    return token.decode("ascii")


def delete_token(identifier: int) -> None:
    token = Token.query.filter_by(id=identifier).all()
    if len(token) != 1:
        raise TokenError("invalid token id {}".format(identifier))
    db.session.delete(token[0])
    db.session.commit()


def generate_token(size: int) -> bytes:
    """
    Generate pseudorandom data and return its representation in hex.
    """
    data = os.urandom(size)
    return binascii.hexlify(data)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
