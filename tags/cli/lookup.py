# coding: utf-8

import click
import yaml

from .. import lookup
from .. import git
from . import main


def lookup_single(lookup_inst, number, yaml_out):
    'Pretty print a single release, in full.'
    if number:
        historic = lookup_inst.release(number)
    else:
        historic = lookup_inst.latest()
    notes = lookup_inst.repo.show_note(historic.ref_name)
    if not yaml_out:
        click.echo('')
        click.echo('Release ', nl=False)
        click.secho("#{0} ".format(historic.number), fg='green', nl=False)
        click.echo('on channel', nl=False)
        click.secho(" {0}".format(historic.channel), fg='cyan', nl=False)
        click.echo(", {0}".format(historic.time.humanize()))
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
        click.echo(notes.get(historic.channel, {}).get(historic.number))
        click.echo('')
        click.echo('Tag:')
        click.secho(" {0}".format(historic.ref_name), fg='yellow')
    else:
        print(yaml.dump(historic.data))


def lookup_listing(lookup_inst, yaml_out):
    'Pretty print a single release, in full.'
    releases = lookup_inst.listing()
    if not yaml_out:
        for historic in releases:
            click.secho("{0}".format(historic.ref_name), fg='yellow', nl=False)
            click.echo(" {0}".format(historic.time.humanize()))
    else:
        print(yaml.dump(historic.data))


@main.command_group.command(name='lookup')
@click.argument('channel')
@click.argument('number', required=False)
@click.option('--yaml', '-y', 'yaml_out', is_flag=True,
              help='Output release data as YAML')
@click.option('--list', '-l', 'list_releases', is_flag=True,
              help='Just list tags and dates')
@click.option('--no-remote', is_flag=True, default=False,
              help='DEBUG: Don’t talk to or touch the remote.')
@click.option('--repo', '-r', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
def lookup_cli(channel, number, yaml_out, list_releases, no_remote, repo):
    'Get the latest release name(s)'
    if no_remote:
        git.Repo.has_remote = lambda *args: False
    lookup_inst = lookup.Lookup(repo, channel)
    if not list_releases:
        return lookup_single(lookup_inst, number, yaml_out)
    return lookup_listing(lookup_inst, yaml_out)
