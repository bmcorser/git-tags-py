'Functions for printing release data and Git output'
import os
import click
import yaml

STATUS_COLOUR = {' M': 'red', ' D': 'red', 'A ': 'green', '??': 'cyan'}


def print_status(status):
    'Print porcelain output colourfully'
    click.echo('  ##')
    for line in status:
        click.secho('  ' + line, fg=STATUS_COLOUR[line[:2]])
    click.echo()


'''
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
'''


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
