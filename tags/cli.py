import datetime
import os
import click
from . import git
from . import message
from . import release as release_
from . import utils

STATUS_COLOUR = {' M': 'red', 'A ': 'green', '??': 'cyan'}


@click.group()
def main():
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
@click.option('--alias', '-a')
@click.option('--release-notes', '-m', default=None)
@click.option('--force', is_flag=True, default=False)
@click.option('--no-remote', is_flag=True, default=False)
def release(pkgs, alias, release_notes, force, no_remote):
    'Tag packages as released'
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
    release_inst.check_existing()
    if not release_notes:
        release_notes = message.capture_message()
        if not utils.filter_empty_lines(release_notes):
            click.echo('Release notes are required')
            click.echo('Bye.')
            exit(1)
    release_inst.notes = release_notes
    release_inst.create_tags()
    click.echo('Release notes:')
    for line in release_notes.split('\n'):
        click.echo('  ' + line)
    if release_inst.alias:
        click.echo('Release alias:')
        click.secho('  ' + alias, fg='green')
        click.echo('Release name:')
        click.secho('  ' + release_inst.commit, fg='cyan')
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


def alias_lookup(alias, pkg):
    filter_ = git.FMT_TAG_ALIAS.format(alias=alias, pkg=pkg, commit='*')
    pkg_tags = git.tag_refs(filter_)
    release_dict = {tag[-7:]: tag for tag in pkg_tags}
    name = git.sort_refs(release_dict.keys())[0]
    tag_contents = git.cat_file((release_dict[name]))
    tagger_line = tag_contents[3].split(' ')
    tag_message = tag_contents[4:]
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


@main.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias', '-a')
@click.option('--number', '-n', default=3)
def lookup(pkgs, alias, number):
    'Get the latest release name(s)'
    if alias:
        filter_ = git.FMT_TAG_ALIAS.format(alias=alias, pkg='*', commit='*')
        alias_tags = git.tag_refs(filter_)
        if not pkgs:
            pkgs = set()
            for tag in alias_tags:
                _, _, pkg, _ = tag.split('/')
                pkgs.add(pkg)
            click.echo("Packages released under alias {0}:".format(alias))
            for pkg in pkgs:
                click.echo('  ' + pkg)
        for pkg in pkgs:
            alias_lookup(alias, pkg)
        exit(os.EX_OK)
    for pkg in pkgs:
        filter_ = git.FMT_TAG.format(pkg=pkg, commit='*')
        pkg_tags = git.tag_refs(filter_)
        release_dict = {tag[-7:]: tag for tag in pkg_tags}
        name = git.sort_refs(release_dict.keys())[0]
        tag_contents = git.cat_file((release_dict[name]))
        tagger_line = tag_contents[3].split(' ')
        tag_message = tag_contents[4:]
        if alias:
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
    exit(os.EX_OK)
