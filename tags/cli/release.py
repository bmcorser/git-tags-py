# coding: utf-8
from __future__ import unicode_literals

import os

import click

from .. import git
from .. import lookup
from .. import release as release_cls
from .. import utils as utils

from .main import main
from . import messages
from . import notes
from . import printing


@main.command(name='release')
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
@click.option('--repo',
              help='Specify repository, defaults to the repo closest to '
                   '$(cwd)')
def release_cli(pkgs, alias, release_notes, force, no_remote, undo, repo):
    messages.release_doc
    if no_remote:
        git.has_remote = lambda: False
    if repo:
        if os.path.isdir(os.path.join(repo, '.git')):
            os.chdir(repo)
        else:
            invalid_repo = (
                'ERROR: You must select a valid Git repository with the '
                '--repo option'
            )
            click.secho(invalid_repo, fg='red', bold=True)
    status = git.status()
    if bool(status) and not force:
        click.echo()
        printing.print_status(status)
        explain = (
            'ERROR: Refusing to release with untracked (??), unstaged ( M) or '
            'uncommitted (A ) files present (see above). Please '
            'stash/commit/reset your changes or override with --force'
        )
        click.secho(explain, fg='red', bold=True)
        exit(os.EX_USAGE)
    release_inst = release_cls.Release(git.head_abbrev(), alias, set(pkgs))
    release_inst.validate_alias()
    # release_inst.validate_pkgs()
    release_inst.validate_unreleased()
    if not release_notes:
        release_notes = notes.capture_message()
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
