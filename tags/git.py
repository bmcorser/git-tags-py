import subprocess
import click

from . import utils


class TagError(Exception):
    'Tell someone a tag exists'
    pass


def get_head_sha1():
    'Return the sha1 hash of the commit at HEAD'
    cmd = ['git', 'rev-parse', 'HEAD']
    return utils.filter_empty_lines(subprocess.check_output(cmd))[0]


def fetch():
    'Fetch tags and commits'
    fetch_cmd = ['git', 'fetch']
    subprocess.check_call(fetch_cmd)
    fetch_tags_cmd = ['git', 'fetch', '--tags']
    subprocess.check_call(fetch_tags_cmd)


def list_tags():
    'List local tags'
    list_tags_cmd = ['git', 'tag', '-l']
    return utils.filter_empty_lines(subprocess.check_output(list_tags_cmd))


def get_tag_list():
    'Fetch tags from remote abd list them'
    fetch()
    return list_tags()


def create_tag(message, name):
    'Create a tag with the passed name and message (default user)'
    cmd = ['git', 'tag', '-a', name, '-m', message]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        if 'unable to resolve ref' in stderr or 'still refs under' in stderr:
            click.echo('Did you use a package name as an alias?')
            raise TagError(name)
        else:
            raise TagError(name)


def delete_tag(name):
    '''
    Try to delete the named tag, echo stderr if it fails for any other reason
    save for the tag not existing.
    '''
    cmd = ['git', 'tag', '-d', name]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        if 'not found' in stderr:
            pass
        else:
            click.echo(stderr)


def push_tags():
    'Push local tags to the remote'
    push_tags_cmd = ['git', 'push', '--tags']
    proc = subprocess.Popen(push_tags_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        click.echo("Error pushing release tags: {0}".format(stderr))
        click.echo('This release will not be available until the tags are '
                   'pushed. You may be able to push the tags manually '
                   'with:\n\n'
                   '  git push --tags')

def status():
    'Return True if there are untracked, unstaged or uncommitted files present'
    cmd = ['git', 'status', '--porcelain']
    return subprocess.check_output(cmd)
