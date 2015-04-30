# coding: utf-8
from __future__ import unicode_literals

import os
import logging

import click
import yaml

from . import git
from . import message
from . import release as release_
from . import utils
from . import lookup

STATUS_COLOUR = {' M': 'red', 'A ': 'green', '??': 'cyan'}


@click.group(invoke_without_command=True)
@click.option('--loglevel', '-l', default='NOTSET',
              help='DEBUG: Set logging level (')
def main(loglevel):
    logging.basicConfig(level=getattr(logging, loglevel.upper()))
    ('Tools for creating and searching git tags\n'
     '\n'
     'Get help on commands with:\n'
     '\n'
     '    tags <command> --help')


def print_status(status):
    'Print porcelain output colourfully'
    for line in utils.filter_empty_lines(status):
        click.secho('  ' + line, fg=STATUS_COLOUR[line[:2]])
    click.echo()


@main.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias', '-a', help='Release packages under an alias')
@click.option('--release-notes', '-m', default=None,
              help='Tell others what this release is. If this option is not '
                   'supplied on the command line, $EDITOR will be used to '
                   'gather release notes')
@click.option('--force', is_flag=True, default=False,
              help='Ignore dirty repo warnings')
@click.option('--no-remote', is_flag=True, default=False,
              help='DEBUG: Don’t publish tags now')
@click.option('--undo', is_flag=True, default=False,
              help='DEBUG: Delete tags for specified release')
def release(pkgs, alias, release_notes, force, no_remote, undo):
    '''
    Cut a new release. Like a boss.

    EXAMPLES:

    Release some packages:

        tag release pkg-a pkg-b

    Release packages under an alias:

        tag release pkg-x pkg-y pkg-z --alias=alphabet-end
    '''
    if no_remote:
        git.has_remote = lambda: False
    status = git.status()
    if bool(status) and not force:
        click.echo()
        print_status(status)
        explain = (
            'ERROR: Refusing to release with untracked (??), unstaged ( M) or '
            'uncommitted (A ) files present (see above). Please '
            'stash/commit/reset your changes or override with --force'
        )
        click.secho(explain, fg='red', bold=True)
        exit(os.EX_USAGE)
    release_inst = release_.Release(git.head_abbrev(), alias, set(pkgs))
    release_inst.validate_alias()
    # release_inst.validate_pkgs()
    release_inst.validate_unreleased()
    if not release_notes:
        release_notes = message.capture_message()
        if not utils.filter_empty_lines(release_notes):
            click.echo('Release notes are required')
            click.echo('Bye.')
            exit(os.EX_NOINPUT)
    release_inst.notes = release_notes
    release_inst.create_tags()
    click.echo('Release notes:')
    for line in release_notes.split('\n'):
        click.echo('  ' + line)
    if release_inst.alias:
        click.echo('Release alias:')
        click.secho('  ' + alias, fg='green')
        click.echo('Packages in this alias:')
        click.echo('  ' + ' '.join(lookup.alias_pkgs(release_inst.alias)))
    else:
        click.echo('Release name:')
        click.secho('  ' + release_inst.commit, fg='green')
        click.echo('Packages included in this release:')
        click.echo('  ' + ' '.join(release_inst.pkgs))
    click.echo('Tags created:')
    for tag in release_inst.new_tags:
        click.secho('  ' + tag, fg='yellow')
    git.push_tags()
    click.echo('Bye.')


'''
    click.echo("Under alias {0}, ".format(alias), nl=False)
    click.echo("{0} was last released at ".format(pkg), nl=False)
    click.secho(name, fg='green', nl=False)
    click.echo(' by ', nl=False)
    click.secho("{0} {1} ".format(tagger_line[1], tagger_line[2]),
                fg='yellow', nl=False)
    tag_date = datetime.datetime.fromtimestamp(float(tagger_line[3]))
    click.secho("({0})".format(tag_date))
    click.echo('Release notes:')
    for line in tag_message:
        click.echo('  ' + line)
'''


def print_releases(releases, yaml_out):
    if yaml_out:
        click.echo(yaml.dump(releases, default_flow_style=False))
        exit(os.EX_OK)
    click.echo('User printing is not yet implemented, try with --yaml')
    exit(os.EX_UNAVAILABLE)


@main.command(name='lookup')
@click.argument('pkgs', nargs=-1)
@click.option('--alias', '-a', help='Packages released under alias')
@click.option('--commit', '-c', help='Packages released at commit')
@click.option('--number', '-n', default=1,
              help='The number of historic releases to return')
@click.option('--yaml', '-y', 'yaml_out', is_flag=True, help='Output as YAML')
def lookup_cli(pkgs, alias, commit, number, yaml_out):
    'Get the latest release name(s)'
    if commit and pkgs:
        click.echo('Either packages or commit. Not both.')
        exit(os.EX_USAGE)
    if alias and pkgs:
        click.echo('Either packages or alias. Not both.')
        exit(os.EX_USAGE)
    '''
    if commit and number:
        click.echo('Only one release will exist for any given commit.')
        exit(os.EX_USAGE)
    '''
    if commit:
        commit_releases = lookup.commit(commit, _alias=alias)
        if not commit_releases:
            click.echo("Nothing released at {0}".format(commit))
            exit(os.EX_DATAERR)
        print_releases(commit_releases, yaml_out)
        exit(os.EX_OK)
    if alias:
        alias_releases = lookup.alias(alias)
        if not alias_releases:
            click.echo("Nothing released under alias {0}".format(alias))
            exit(os.EX_DATAERR)
        print_releases(alias_releases, yaml_out)
        exit(os.EX_OK)
    if not pkgs:
        click.echo('You didn’t pass any arguments or options, try --help')
        exit(os.EX_USAGE)
    pkg_releases = {}
    for pkg in pkgs:
        pkg_releases[pkg] = lookup.package(pkg)
    if not pkg_releases:
        click.echo("No releases for package {0}".format(alias))
        exit(os.EX_DATAERR)
    print_releases(pkg_releases, yaml_out)
    exit(os.EX_OK)
