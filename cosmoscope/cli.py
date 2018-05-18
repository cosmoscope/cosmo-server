"""Console script for cosmoscope."""
import sys
import click

from .server import launch


@click.command()
@click.option('--server-address', default="tcp://127.0.0.1:4242", help="Server IP address.")
@click.option('--publisher-address', default="tcp://127.0.0.1:4243", help="Publisher IP address.")
def main(server_address=None, publisher_address=None):
    """Console interface for the cosmoscope server."""
    launch(server_address, publisher_address)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
