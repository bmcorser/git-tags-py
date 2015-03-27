import functools
import click
from . import git
from . import message
from . import naming
from . import utils

def check_existing(tags, existing_tags):
    chkd_tags = []
    for tag in tags:
        if tag in existing_tags:
            click.echo("WARNING: {0} has already been released".format(tag))
            if not click.confirm('Do you want to continue?'):
                exit('Bye.')
        else:
            chkd_tags.append(tag)
    if not chkd_tags:
        exit('Nothing to release.')
    return chkd_tags

@click.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias')
def main(pkgs, alias):
    pkgs = set(pkgs)
    head_sha1 = git.get_head_sha1()[:7]
    new_tags = check_existing(
        naming.format_tags(pkgs, head_sha1, alias),
        git.get_tag_list()
    )
    release_notes = message.capture_message()
    if not utils.filter_empty_lines(release_notes):
        exit('Release notes are required')
    map(functools.partial(git.create_tag, release_notes), new_tags)
    click.echo("Release marked on {0}".format(head_sha1))
    click.echo('Packages included in this release:')
    for pkg in pkgs:
        click.echo('  ' + pkg)
    if alias:
        fmt_string = "This release can be referred to by the alias: {0}"
        click.echo(fmt_string.format(alias))
