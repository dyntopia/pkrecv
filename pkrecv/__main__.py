import sys

import click

from . import app, wsgi
from .models import token


@click.group()
@click.option("--config", default="~/.pkrecv.py")
@click.pass_context
def cli(ctx: click.Context, config: str) -> None:
    try:
        ctx.obj["app"] = app.init_app(config)
    except app.AppError as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        sys.exit(1)


@cli.command("add-token")
@click.option("--role", required=True)
@click.option("--description")
def add_token(role: str, description: str) -> None:
    try:
        t = token.add_token(role, description)
    except token.TokenError as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        sys.exit(1)
    print("Token: {}".format(t))


@cli.command()
@click.pass_context
def serve(ctx: click.Context) -> None:
    options = ctx.obj["app"].config.get("GUNICORN", {})
    wsgi.Gunicorn(ctx.obj["app"], options).run()


def main() -> int:
    cli(obj={})  # pylint: disable=E1120,E1123
    return 0
