# coding: utf-8
from __future__ import unicode_literals

import click
import yaml

from .. import lookup
from .. import git
from . import main


@main.command_group.command(name='lookup')
@click.argument('channel')
@click.argument('number', required=False)
@click.option('--yaml', '-y', 'yaml_out', is_flag=True,
              help='Output release data as YAML')
@click.option('--no-remote', is_flag=True, default=False,
              help='DEBUG: Don’t talk to or touch the remote.')
@click.option('--repo', '-r', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
def lookup_cli(channel, number, yaml_out, no_remote, repo):
    'Get the latest release name(s)'
    if no_remote:
        git.Repo.has_remote = lambda *args: False
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
        click.echo('')
        if pkgs['unchanged']:
            click.echo('Unchanged:')
            for path, tree in pkgs['unchanged'].items():
                click.echo("  {0} ".format(path))
        click.echo('')
        click.echo('Notes:')
        click.echo(repo.show_note(historic.ref_name)[historic.channel][historic.number])
        click.echo('')
    else:
        print(yaml.dump(historic.data))
