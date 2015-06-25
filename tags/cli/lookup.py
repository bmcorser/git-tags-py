# coding: utf-8
from __future__ import unicode_literals

import os
import pprint

import click

from .. import lookup
from . import main
from .. import git


@main.command_group.command(name='lookup')
@click.argument('channel')
@click.argument('number', required=False)
@click.option('--repo', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
def lookup_cli(channel, number, repo):
    'Get the latest release name(s)'
    os.chdir(repo)  # for subprocess calls to git
    head = git.head_abbrev()
    repo_root = git.repo_root(repo)
    L = lookup.Lookup(repo_root, head, channel)
    if number:
        pprint.pprint(L.release(number))
    else:
        pprint.pprint(L.latest())
