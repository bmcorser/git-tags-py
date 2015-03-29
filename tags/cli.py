import functools
import click
from . import git
from . import message
from .release import Release
from . import utils

@click.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias', '-a')
@click.option('--release-notes', '-m', default=None)
@click.option('--force', is_flag=True, default=False)
def main(pkgs, alias, release_notes, force):
    status = git.status()
    if bool(status) and not force:
        click.echo(status)
        click.secho('Refusing to release with untracked, unstaged or '
                    'uncommitted files present (see above). Please '
                    'commit/reset your changes or override with --force',
                    fg='red', bold=True)
        exit(1)
    release = Release(git.get_head_sha1()[:7], alias, set(pkgs))
    release.validate_pkgs()
    release.check_existing()
    if not release_notes:
        release_notes = message.capture_message()
        if not utils.filter_empty_lines(release_notes):
            click.echo('Release notes are required')
            click.echo('Bye.')
            exit(1)
    try:
        map(functools.partial(git.create_tag, release_notes), release.tags)
    except git.TagError as err_tag:
        click.secho("Error creating tag {0}".format(err_tag), fg='red', bold=True)
        click.echo('Attempting to clean up ...')
        map(git.delete_tag, release.tags)
        click.echo('Bye.')
        exit(1)
    click.echo('Release notes:')
    for line in release_notes.split('\n'):
        click.echo('  ' + line)
    if release.alias:
        click.echo('Release alias:')
        click.secho('  ' + alias, fg='green')
        click.echo('Release name:')
        click.secho('  ' + release.commit, fg='cyan')
    else:
        click.echo('Release name:')
        click.secho('  ' + release.commit, fg='green')
    click.echo('Packages included in this release:')
    click.echo('  ' + ' '.join(release.pkgs))
    click.echo('Tags created:')
    for tag in release.tags:
        click.secho('  ' + tag, fg='yellow')
    git.push_tags()
    click.echo('Bye.')
