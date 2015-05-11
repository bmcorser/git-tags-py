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
@click.option('--repo', callback=main.validate_repo,
              help='Specify repository, defaults to the cwd')
@click.option('--yaml', '-y', 'yaml_out', is_flag=True, help='Output as YAML')
def lookup_cli(pkgs, alias, commit, number, yaml_out, repo):
    'Get the latest release name(s)'
    os.chdir(repo)  # for subprocess calls to git
    if commit and pkgs:
        printing.error('Either packages or commit. Not both.')
        exit(os.EX_USAGE)
    if alias and pkgs:
        printing.error('Either packages or alias. Not both.')
        exit(os.EX_USAGE)
    '''
    if commit and number:
        click.echo('Only one release will exist for any given commit.')
        exit(os.EX_USAGE)
    '''
    if commit:
        try:
            commit_releases = lookup.commit(commit, _alias=alias)
        except lookup.CommitNotFound as exc:
            printing.error(exc)
            exit(os.EX_DATAERR)
        printing.print_releases(commit_releases, yaml_out)
        exit(os.EX_OK)
    if alias:
        try:
            alias_releases = lookup.alias(alias)
        except lookup.AliasNotFound as exc:
            printing.error(exc)
            exit(os.EX_DATAERR)
        printing.print_releases(alias_releases, yaml_out)
        exit(os.EX_OK)
    if not pkgs:
        click.echo('You didn’t pass any arguments or options, try --help')
        exit(os.EX_USAGE)
    pkg_releases = {}
    for pkg in pkgs:
        try:
            pkg_releases[str(pkg)] = lookup.package(pkg)
        except lookup.PackageNotFound as exc:
            printing.error(exc)
            exit(os.EX_DATAERR)
    printing.print_releases(pkg_releases, yaml_out)
    exit(os.EX_OK)
