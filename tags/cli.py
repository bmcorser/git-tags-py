import click
from . import git
from . import message


@click.command()
@click.argument('pkgs', nargs=-1)
@click.option('--alias')
def main(pkgs, alias):
    head_sha1 = git.get_head_sha1()
    release_notes = message.capture_message()
    import ipdb;ipdb.set_trace()
