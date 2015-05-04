# coding: utf-8
from __future__ import unicode_literals

import logging
import click

from .. import git


@click.group(invoke_without_command=True)
@click.option('--loglevel', '-l', default='WARN',
              help='DEBUG: Set logging level for program.')
def command_group(loglevel):
    '''
    Tools for creating and searching git tags

    Get help on commands with:

        tags <command> --help
    '''
    logging.basicConfig(level=getattr(logging, loglevel.upper()))


def validate_repo(ctx, param, value):
    'Validate the value passed to the --repo option looks like a Git repo'
    if not git.is_repo(value):
        raise click.BadParameter('That\'s not a Git repository!')
    return value
