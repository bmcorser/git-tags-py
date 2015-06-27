# coding: utf-8
from __future__ import unicode_literals

import logging
import os

import click

from .. import git


@click.group(name='tag', invoke_without_command=True)
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
    if value is None:
        value = os.getcwd()
    if not git.is_repo(value):
        raise click.BadParameter('That\'s not a Git repository!')
    return git.Repo(value)
