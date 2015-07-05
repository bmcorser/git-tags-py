# coding: utf-8
from __future__ import unicode_literals

import os

import click

from .. import git
from .. import release as release_cls
from .. import utils as utils

from . import main
from . import messages
from . import notes
from . import printing


def validate_channel(ctx, param, value):
    'If no channel is passed, check env for value, if nothing’s there, raise'
    if value:
        if os.path.sep in value:
            raise click.BadParameter('Channel names may not contain path separator')
        return value
    env_channel = os.environ.get('GIT_TAGS_PY_CHANNEL')
    if env_channel is None:
        raise click.BadParameter('Either pass a channel or set '
                                 'GIT_TAGS_PY_CHANNEL to the name of the '
                                 'channel you wish to release on by default.')
    return env_channel


@main.command_group.command(name='release')
@click.option('--channel', '-c', callback=validate_channel,
              help='Release channel, defaults to GIT_TAGS_PY_CHANNEL')
@click.option('--release-notes', '-m', default=None,
              help='Tell others what this release is. If this option is not '
                   'supplied on the command line, $EDITOR will be used to '
                   'gather release notes')
@click.option('--force', is_flag=True, default=False,
              help='Ignore dirty repo warnings')
@click.option('--no-remote', is_flag=True, default=False,
              help='DEBUG: Don’t talk to or touch the remote.')
@click.option('--repo', '-r', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
@click.option('--yaml', '-y', 'yaml_out', is_flag=True,
              help='Output release data as YAML')
def release_cli(channel, release_notes, force, no_remote, yaml_out, repo):
    '''
    Cut a new release. Like a boss.

    EXAMPLES:

    Release to default channel (development):

        tag release

    Release to named channel:

        tag release -c production
    '''
    if no_remote:
        git.Repo.has_remote = lambda *args: False
    status = repo.status()
    if bool(status) and not force:
        click.echo()
        printing.print_status(status)
        printing.error(messages.release_repo_dirty)
        exit(os.EX_USAGE)
    release_inst = release_cls.Release(repo, channel)
    if not release_inst.changed:
        printing.error('No packages changed, nothing to release')
        exit(os.EX_DATAERR)
    if not release_notes:
        prev_ref_name = getattr(release_inst.previous, 'ref_name', '')
        _, (diff, _) = repo.run(['diff', prev_ref_name, release_inst.ref_name])
        release_notes = notes.capture_message('\n'.join(diff))
        import ipdb;ipdb.set_trace()
        if not utils.filter_empty_lines(release_notes):
            click.echo('Release notes are required')
            click.echo('Bye.')
            exit(os.EX_NOINPUT)
    release_inst.create_tag()
    git.release_note(repo, release_inst, release_notes)
    push_ok, stderr = repo.push_ref(release_inst.ref_name)
    click.echo('')
    if not push_ok:
        click.echo("Error pushing release tags: {0}".format(stderr))
        click.echo('This release will not be available until the tags are '
                   'pushed. You may be able to push the tags manually '
                   'with:\n\n'
                   "  git push origin {0}".format(release_inst.ref_name))

    notes_ref = git.REF_NS.format(kind='notes', name=git.NS)
    push_ok, stderr = repo.push_ref(notes_ref)
    if not push_ok:
        click.echo("Error pushing release notes: {0}".format(stderr))
        click.echo('You may be able to push the notes manually '
                   'with:\n\n'
                   "  git push origin {0}".format(notes_ref))
    printing.print_releases([release_inst], yaml_out)
