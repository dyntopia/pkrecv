from .cli import cli


def main() -> int:
    cli()  # pylint: disable=E1120
    return 0
