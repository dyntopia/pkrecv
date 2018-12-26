import datetime
from typing import Any, List

from sqlalchemy import DateTime, ForeignKey, Integer, String

from .db import Model, column, db


class ServerError(Exception):
    pass


class Server(Model):
    id = column(Integer, primary_key=True)
    ip = column(String(45))  # http://www.ipuptime.net/ipv4mapped.aspx
    port = column(Integer, default=22)
    key_type = column(String(32))
    public_key = column(String(4096))
    created = column(DateTime, default=datetime.datetime.utcnow)
    token_id = column(Integer, ForeignKey("token.id"))


def get_servers(**filters: Any) -> List[Server]:
    """
    Retrieve a list of servers.
    """
    return [s.as_dict for s in Server.query.filter_by(**filters).all()]


def add_server(ip: str, port: int, public_key: str, token_id: int) -> None:
    """
    Add a server.
    """
    db.session.add(Server(
        ip=ip,
        port=port,
        key_type=get_key_type(public_key),
        public_key=public_key.strip(),
        token_id=token_id
    ))
    db.session.commit()


def get_key_type(public_key: str) -> str:
    """
    Retrieve the key type for a public key.
    """
    try:
        return public_key.split()[0].lstrip("ssh-")
    except IndexError:
        raise ServerError("could not determine key type")
