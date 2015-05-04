import logging
import click
from . import messages


@click.group(invoke_without_command=True)
@click.option('--loglevel', '-l', default='WARN',
              help='DEBUG: Set logging level (')
def main(loglevel):
    messages.main_doc
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
