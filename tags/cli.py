import functools
import click
from . import git
from . import message
from .release import Release
from . import utils

@click.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias')
def main(pkgs, alias):
    release = Release(git.get_head_sha1()[:7], alias, set(pkgs))
    release.check_existing()
    release_notes = message.capture_message()
    if not utils.filter_empty_lines(release_notes):
        exit('Release notes are required', code=1)
    try:
        map(functools.partial(git.create_tag, release_notes), release.tags)
    except git.TagError as err_tag:
        click.echo("Error creating tag {0}".format(err_tag))
        click.echo('Attempting to clean up ...')
        map(git.delete_tag, release.tags)
        exit(code=1)
    if release.alias:
        click.echo("Release alias: {0}".format(alias))
        click.echo("Release name:  {0}".format(release.commit))
    else:
        click.echo("Release name: {0}".format(release.commit))
    click.echo('Packages included in this release:')
    for pkg in release.pkgs:
        click.echo('  ' + pkg)
