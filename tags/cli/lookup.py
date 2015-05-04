# coding: utf-8
from __future__ import unicode_literals

import os

import click

from .. import lookup
from . import printing
from . import main


@main.command_group.command(name='lookup')
@click.argument('pkgs', nargs=-1)
@click.option('--alias', '-a', help='Packages released under alias')
@click.option('--commit', '-c', help='Packages released at commit')
@click.option('--number', '-n', default=1,
              help='The number of historic releases to return')
@click.option('--repo', default=os.getcwd(), callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
@click.option('--yaml', '-y', 'yaml_out', is_flag=True, help='Output as YAML')
def lookup_cli(pkgs, alias, commit, number, yaml_out, repo):
    'Get the latest release name(s)'
    os.chdir(repo)  # for subprocess calls to git
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
        printing.print_releases(commit_releases, yaml_out)
        exit(os.EX_OK)
    if alias:
        alias_releases = lookup.alias(alias)
        if not alias_releases:
            click.echo("Nothing released under alias {0}".format(alias))
            exit(os.EX_DATAERR)
        printing.print_releases(alias_releases, yaml_out)
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
    printing.print_releases(pkg_releases, yaml_out)
    exit(os.EX_OK)
