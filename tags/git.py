import string
import logging
import os
import subprocess

import click

from . import utils

FMT_NS = 'releases/{release}'
FMT_TAG = FMT_NS.format(release='{pkg}/{commit}')
FMT_TAG_ALIAS = FMT_NS.format(release='{alias}/{pkg}/{commit}')

LOGGER = logging.getLogger(__name__)


def log_cmd(cmd):
    'Log the invocation of a command'
    LOGGER.debug("Invoking {cmd}".format(cmd=' '.join(cmd)))


class TagError(Exception):
    'Tell someone a tag exists'
    pass


def has_remote():
    'Test if repo has a remote defined'
    remote_cmd = ['git', 'remote']
    log_cmd(remote_cmd)
    output = subprocess.check_output(remote_cmd)
    return bool(utils.filter_empty_lines(output))


def head_abbrev(directory=None):
    '''
    Return the unambiguous abbreviated sha1 hash of the commit at HEAD,
    optionally for a directory.

    Note: The abbreviated hash can be of variable length.
    '''
    cmd = ['git', 'rev-list', '-1', 'HEAD', '--abbrev-commit']
    log_cmd(cmd)
    if directory:
        cmd.extend(['--', directory])
    return utils.filter_empty_lines(subprocess.check_output(cmd))[0]


def fetch():
    'Fetch tags and commits'
    if not has_remote():
        return
    fetch_cmd = ['git', 'fetch']
    log_cmd(fetch_cmd)
    subprocess.check_call(fetch_cmd)
    fetch_tags_cmd = ['git', 'fetch', '--tags']
    log_cmd(fetch_tags_cmd)
    subprocess.check_call(fetch_tags_cmd)


def create_tag(message, name):
    'Create a tag with the passed name and message (default user)'
    cmd = ['git', 'tag', '-a', name, '-m', message]
    log_cmd(cmd)
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
    log_cmd(cmd)
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
    if not has_remote():
        return
    push_tags_cmd = ['git', 'push', '--tags']
    log_cmd(push_tags_cmd)
    proc = subprocess.Popen(push_tags_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        return None, stderr
    return True, None


def status():
    'Return True if there are untracked, unstaged or uncommitted files present'
    cmd = ['git', 'status', '--porcelain']
    log_cmd(cmd)
    return subprocess.check_output(cmd)


def channel_refs(channel):
    'Return the short refs of tags in the passed namespace'
    cmd = [
        'git',
        'for-each-ref',
        '--format',
        '%(refname:short): %(objectname:short)',
        "refs/tags/releases/{0}/*".format(channel),
    ]
    log_cmd(cmd)
    return utils.filter_empty_lines(subprocess.check_output(cmd))


def cat_file(ref):
    'Call cat-file -p on the ref passed'
    cmd = ['git', 'cat-file', '-p', ref]
    log_cmd(cmd)
    return utils.filter_empty_lines(subprocess.check_output(cmd))


def tagger_line_tokens(tokens):
    'Return the tagger name, email, time and timezone for a tagger line'
    for index, token in enumerate(tokens[1:]):
        if '<' in token and '>' in token:
            e_ix = index + 1  # email position
            break
    return (' '.join(tokens[1:e_ix]),) + tuple(tokens[e_ix:])


def tag_dict(tag):
    'Return the contents of a tag as a dictionary'
    contents = cat_file(tag)
    tagger, email, time, timezone = tagger_line_tokens(contents[3].split(' '))
    tag_message = '\n'.join(contents[4:])
    return {
        'tag': tag,
        'tagger_name': tagger,
        'tagger_email': email.strip('<>'),
        'time': time,
        'timezone': timezone,
        'message': tag_message
    }


def is_repo(repo_dir):
    '''
    Return True if the passed irectory looks like a Git repository, otherwise
    return False.
    '''
    if os.path.isdir(os.path.join(repo_dir, '.git')):
        return True
    return False


def attrs_dict(directory):
    'Return the attributes for a directory as a dict'
    attr_cmd = ['git', 'check-attr', '-a', directory]
    log_cmd(attr_cmd)
    output = subprocess.check_output(attr_cmd)
    ret_dict = {}
    for line in utils.filter_empty_lines(output):
        _, name, value = line.split(': ')
        ret_dict[name] = value
    return ret_dict


def recurse_tree(root, remaining):
    if not len(remaining):
        return root
    for _, git_type, oid, name in map(string.split, cat_file(root)):
        if name == remaining[0]:
            return recurse_tree(oid, remaining[1:])


def path_tree(path):
    'Get the object ID for the directory at `path`'
    root = cat_file('HEAD')[0].split()[1]
    return recurse_tree(root, path.split('/'))
