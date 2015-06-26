import string
import logging
import os
import subprocess
import yaml

import click

from . import utils

NS = 'release'
RELEASE_NS = "{ns}/{release}".format(ns=NS, release='{name}')
TAG_NS = 'refs/tags/{name}'
NOTE_NS = "refs/notes/{ns}".format(ns=NS)

LOGGER = logging.getLogger(__name__)


class NoTree(Exception):
    'No tree object found in the repo'
    pass


def log_cmd(cmd):
    'Log the invocation of a command'
    LOGGER.debug("Invoking {cmd}".format(cmd=' '.join(cmd)))


def release_tag(channel, number=None):
    'Return either a release tag or channel glob'
    if number:
        name = "{channel}/{number}".format(channel=channel, number=number)
    else:
        name = "{channel}/*".format(channel=channel)
    return RELEASE_NS.format(name=name)


def release_ref(channel, number=None):
    'Return either a full ref or channel glob'
    tag_name = release_tag(channel, number)
    return TAG_NS.format(name=tag_name)


class TagError(Exception):
    'Tell someone a tag exists'
    pass


def repo_root(repo_path):
    'Get the root directory of a repository'
    root_cmd = ['git', 'rev-parse', '--show-toplevel']
    log_cmd(root_cmd)
    output = subprocess.check_output(root_cmd)
    return output.strip()


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
    cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
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


def push_ref(ref):
    'Push local tags to the remote'
    if not has_remote():
        return
    push_tags_cmd = ['git', 'push', 'origin', ref]
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


def refs_glob(glob):
    'Return the short refs of tags in the passed namespace'
    '%(refname:short): %(objectname:short)',
    fetch()
    cmd = [
        'git',
        'for-each-ref',
        '--format',
        '%(refname:short)',
        glob
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
    body = yaml.load('\n'.join(contents[4:]))
    return {
        'tag': tag,
        'tagger_name': tagger,
        'tagger_email': email.strip('<>'),
        'time': time,
        'timezone': timezone,
        'body': body
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
    raise NoTree()


def path_tree(path):
    'Get the object ID for the directory at `path`'
    root = cat_file('HEAD')[0].split()[1]
    try:
        return recurse_tree(root, path.split('/'))
    except NoTree:
        raise NoTree("No tree found for path: {0}".format(path))


def checkout(commitish):
    'Check out the commitish'
    checkout_cmd = ['git', 'checkout', commitish]
    log_cmd(checkout_cmd)
    proc = subprocess.Popen(checkout_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if proc.wait() > 0:
        _, stderr = proc.communicate()
        raise Exception('check out error')


def note(message):
    'Add a note to the commit at HEAD'
    note_cmd = ['git', 'notes', '--ref', NS, 'add', '-m', message]
    log_cmd(note_cmd)
    subprocess.check_call(note_cmd)
