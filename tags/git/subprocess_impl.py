import subprocess

from . import utils

def get_head_sha1():
    'Return the sha1 hash of the commit at HEAD'
    cmd = ['git', 'rev-parse', 'HEAD']
    return utils.filter_output(subprocess.check_output(cmd))[0]


def get_tag_list():
    'Return all the tags in the repo'
    cmd = ['git', 'tag', '-l']
    return utils.filter_output(subprocess.check_output(cmd))


def create_tag(name, message):
    'Create a tag with the passed name and message (default user)'
    cmd = ['git', 'tag', '-a', name, '-m', message]
    subprocess.check_call(cmd)

if __name__ == '__main__':
    get_tag_list()
