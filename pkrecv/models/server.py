import base64
import binascii
import datetime
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import validates

from .db import Model, column, db


class ServerError(Exception):
    pass


class Server(Model):
    id = column(Integer, primary_key=True)
    ip = column(String(45))  # http://www.ipuptime.net/ipv4mapped.aspx
    port = column(Integer, default=22)
    key_type = column(String(32))
    key_data = column(String(4096))
    key_comment = column(String(4096))
    created = column(DateTime, default=datetime.datetime.utcnow)
    token_id = column(Integer, ForeignKey("token.id"))

    # pylint: disable=no-self-use
    @validates("key_type")
    def validate_key_type(self, _: str, key_type: str) -> str:
        # From sshd(8).
        key_types = [
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-ed25519",
            "ssh-dss",
            "ssh-rsa"
        ]
        if key_type not in key_types:
            raise ServerError("{} is not a valid key type".format(key_type))
        return key_type

    @validates("key_data")
    def validate_key_data(self, _: str, key_data: str) -> str:
        try:
            base64.b64decode(key_data)
        except binascii.Error:
            raise ServerError("{} is not a valid key".format(key_data))
        return key_data
    # pylint: enable=no-self-use


def get_servers(**filters: Any) -> List[Server]:
    """
    Retrieve a list of servers.
    """
    return [s.as_dict for s in Server.query.filter_by(**filters).all()]


def add_server(ip: str, port: int, public_key: str, token_id: int) -> None:
    """
    Add a server.
    """
    key_type, key_data, key_comment = split_key(public_key)

    db.session.add(Server(
        ip=ip,
        port=port,
        key_type=key_type,
        key_data=key_data,
        key_comment=key_comment,
        token_id=token_id
    ))
    db.session.commit()


def split_key(public_key: str) -> List[str]:
    """
    Split a public key into a list of [type, data, comment].
    """
    components = public_key.split()
    if len(components) == 3:
        return components
    if len(components) == 2:
        return components + [""]
    raise ServerError("invalid public key")
