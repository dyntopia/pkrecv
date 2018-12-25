import sys

import click

from . import app, token


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
    t = token.add_token(role, description)
    print("Token: {}".format(t))


def main() -> int:
    cli(obj={})  # pylint: disable=E1120,E1123
    return 0
