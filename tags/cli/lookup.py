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
@click.option('--yaml', '-y', 'yaml_out', help='Output release data as YAML')
@click.option('--repo', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
def lookup_cli(channel, number, yaml_out, repo):
    'Get the latest release name(s)'
    lookup_inst = lookup.Lookup(repo, channel)
    if number:
        historic = lookup_inst.release(number)
    else:
        historic = lookup_inst.latest()
    if not yaml_out:
        click.echo('')
        click.echo('Release ', nl=False)
        click.secho("#{0} ".format(historic.number), fg='green', nl=False)
        click.echo('on channel', nl=False)
        click.secho(" {0}".format(historic.channel), fg='cyan')
        click.echo('')
        click.echo('Changed:')
        pkgs = historic.data['body']['packages']
        for path, tree in pkgs['changed'].items():
            click.echo("  {0} ".format(path))
        if pkgs['unchanged']:
            click.echo('Unchanged:')
            for path, tree in pkgs['unchanged'].items():
                click.echo("  {0} ".format(path))
        click.echo('')
        click.echo('Notes:')
        click.echo(repo.show_note(historic))
        click.echo('')
