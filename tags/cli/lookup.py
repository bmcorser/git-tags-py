# coding: utf-8
from __future__ import unicode_literals

import os
import pprint

import click

from .. import lookup
from . import printing
from . import main


@main.command_group.command(name='lookup')
@click.argument('channel')
@click.argument('number', required=False)
@click.option('--repo', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
def lookup_cli(channel, number, repo):
    'Get the latest release name(s)'
    os.chdir(repo)  # for subprocess calls to git
    if number:
        pprint.pprint(lookup.channel_release(channel, number))
    else:
        pprint.pprint(lookup.channel_latest(channel))
