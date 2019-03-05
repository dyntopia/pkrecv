import sys

import click
from munch import Munch

from . import app, config, wsgi
from .models import token


@click.group()
@click.option("--config-file", default="~/.pkrecv.ini")
@click.pass_context
def cli(ctx: click.Context, config_file: str) -> None:
    cfg = config.Config()
    try:
        cfg.read(config_file)
    except config.ConfigError as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        sys.exit(1)

    try:
        flask = app.init_app(cfg.get_section("flask", {}))
    except app.AppError as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        sys.exit(1)

    gunicorn = wsgi.Gunicorn(flask, cfg.get_section("gunicorn", {}))
    ctx.obj = Munch(gunicorn=gunicorn)


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
    ctx.obj.gunicorn.run()
