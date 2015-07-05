'Functions for printing release data and Git output'
import os
import click
import yaml


def print_status(status):
    'Print porcelain output colourfully'
    click.echo('  ##')
    for line in status:
        click.secho('  ', nl=False)
        for (i, colour) in ((0, 'green'), (1, 'red')):
            char = line[i]
            if char == '?':
                colour = 'cyan'
            click.secho(line[i], fg=colour, nl=False)
        click.echo(line[2:])
    click.echo()


def print_releases(releases, yaml_out):
    'Print release data to YAML (or soon to the CLI)'
    if yaml_out:
        click.echo(yaml.dump(releases, default_flow_style=False))
        exit(os.EX_OK)
    click.echo('User printing is not yet implemented, try with --yaml')
    exit(os.EX_UNAVAILABLE)


def error(message):
    'Print something in red with big ERROR prefix'
    click.secho("ERROR: {0}".format(message), fg='red', bold=True)
