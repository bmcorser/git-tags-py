import subprocess

from . import utils


class TagExists(Exception):
    'Tell someone a tag exists'
    pass


def get_head_sha1():
    'Return the sha1 hash of the commit at HEAD'
    cmd = ['git', 'rev-parse', 'HEAD']
    return utils.filter_empty_lines(subprocess.check_output(cmd))[0]


def get_tag_list():
    'Return all the tags in the repo'
    fetch_cmd = ['git', 'fetch']
    subprocess.check_call(fetch_cmd)
    fetch_tags_cmd = ['git', 'fetch', '--tags']
    subprocess.check_call(fetch_tags_cmd)
    list_tags_cmd = ['git', 'tag', '-l']
    return utils.filter_empty_lines(subprocess.check_output(list_tags_cmd))


def create_tag(message, name):
    'Create a tag with the passed name and message (default user)'
    cmd = ['git', 'tag', '-a', name, '-m', message]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        if 'already exists' not in str(e):
            raise
        raise TagExists('That tag exists')
