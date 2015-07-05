'Functions for printing release data and Git output'
import collections
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
    'Print release data to YAML or colourfully to the CLI'
    if yaml_out:
        out_dict = collections.defaultdict(dict)
        for release in releases:
            out_dict[release.channel][release.number] = release.data
        click.echo(yaml.dump(out_dict, default_flow_style=False))
        exit(os.EX_OK)
    for release in releases:
        click.echo('Release ', nl=False)
        click.secho("#{0} ".format(release.number), fg='green', nl=False)
        click.echo('on channel', nl=False)
        click.secho(" {0}".format(release.channel), fg='cyan')
        click.echo('')
        click.echo('Included:')
        for path, _ in release.changed.items():
            click.echo("  {0} ".format(path))
        click.echo('')
        click.echo('Tag: ', nl=False)
        click.secho(release.ref_name, fg='yellow')
        click.echo('')
    exit(os.EX_OK)


def error(message):
    'Print something in red with big ERROR prefix'
    click.secho("ERROR: {0}".format(message), fg='red', bold=True)
