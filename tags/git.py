import string
import os
import subprocess
import yaml

import click

from . import utils

NS = 'release'
TAG_FMT = '{channel}/{number}'
TAG_NS = '{ns}/{tag}'
REF_NS = 'refs/{kind}/{name}'


class NoTree(Exception):
    'No tree object found in the repo'
    pass


class CreateTagError(Exception):
    'Could not create tag'
    pass

class CheckoutError(Exception):
    'Tell someone a tag exists'
    pass



def release_tag(channel, number=None):
    'Return either a release tag or channel glob'
    if number:
        tag = TAG_FMT.format(channel=channel, number=number)
    else:
        tag = TAG_FMT.format(channel=channel, number='*')
    return TAG_NS.format(ns=NS, tag=tag)


def release_number(ref):
    'Extract the number for a release from a tag name'
    return int(ref.split('/')[-1])


def release_note(repo, release, message):
    'Add a note to the commit for the release passed'
    repo.checkout(release.ref_name)
    note_dict = {str(release.channel): {release.number: str(message)}}
    cmd = ['notes', '--ref', NS, 'show']
    retcode, (existing_note, err) = repo.run(cmd)
    if retcode > 0 and 'No note found' in err[0]:
        note = yaml.dump(note_dict, default_flow_style=False)
    else:
        existing_note = yaml.load('\n'.join(existing_note))
        note_dict = utils.recursive_update(existing_note, note_dict)
        note = yaml.dump(existing_note, default_flow_style=False)
    cmd = ['notes', '--ref', NS, 'add', '-f', '-m', note]
    retcode, (out, err) = repo.run(cmd)
    repo.checkout()


def is_repo(repo_dir):
    '''
    Return True if the passed irectory looks like a Git repository, otherwise
    return False.
    '''
    if os.path.isdir(os.path.join(repo_dir, '.git')):
        return True
    return False


def release_ref(channel, number=None):
    'Return either a full ref or channel glob'
    name = release_tag(channel, number)
    return REF_NS.format(kind='tags', name=name)


def tagger_line_tokens(tokens):
    'Return the tagger name, email, time and timezone for a tagger line'
    for index, token in enumerate(tokens[1:]):
        if '<' in token and '>' in token:
            e_ix = index + 1  # email position
            break
    return (' '.join(tokens[1:e_ix]),) + tuple(tokens[e_ix:])


def run(directory, git_subcommand, **popen_kwargs):
    '''
    Start a process to run the passed git subcommand in the passed directory
    Returns the return code and formatted output in a tuple nest like this:

        (returncode, (out, err))

    '''
    proc = subprocess.Popen(['git'] + git_subcommand,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=directory,
                            **popen_kwargs)
    retcode = proc.wait()
    return retcode, map(utils.filter_empty_lines, proc.communicate())


class Repo(object):

    def __init__(self, directory):
        root_cmd = ['rev-parse', '--show-toplevel']
        retcode, (out, err) = run(directory, root_cmd)
        if retcode > 0:
            raise Exception('Not a repo?')
        self.root = out[0]
        branch_cmd = ['symbolic-ref', '--quiet', 'HEAD']
        retcode, (out, err) = run(directory, branch_cmd)
        self.start_branch = out[0].lstrip('refs/heads/')

    def run(self, cmd):
        'Run a git command in this repo, just closes self.root'
        return run(self.root, cmd)

    def has_remote(self):
        'Test if repo has a remote defined'
        retcode, (out, err) = self.run(['remote'])
        return bool(out)

    def head_abbrev(self):
        '''
        Return the unambiguous abbreviated sha1 hash of the commit at HEAD,
        optionally for a directory.

        Note: The abbreviated hash can be of variable length.
        '''
        retcode, (out, err) = self.run(['rev-parse', '--abbrev-ref', 'HEAD'])
        return out[0]

    def fetch(self):
        'Fetch tags and commits'
        if not self.has_remote():
            return
        self.run(['fetch'])
        self.run(['fetch', '--tags'])

    def create_tag(self, message, name):
        'Create a tag with the passed name and message (default user)'
        retcode, (out, err) = self.run(['tag', '-a', name, '-m', message])
        if retcode > 0:
            if 'unable to resolve ref' in err or 'still refs under' in err:
                click.echo('Did you use a package name as an alias?')
                raise CreateTagError(name)
            else:
                raise CreateTagError(name)

    def delete_tag(self, name):
        '''
        Try to delete the named tag, echo stderr if it fails for any other
        reason save for the tag not existing.
        '''
        retcode, (out, err) = self.run(['tag', '-d', name])
        if retcode > 0:
            if 'not found' in err:
                pass
            else:
                click.echo(err)

    def push_ref(self, ref):
        'Push local tags to the remote'
        if not self.has_remote():
            return
        retcode, (out, err) = self.run(['push', 'origin', ref])
        if retcode:
            return None, err
        return True, None

    def status(self):
        'Return True if there are untracked, unstaged or uncommitted files present'
        retcode, (out, err) = self.run(['status', '--porcelain'])
        return out

    def refs_glob(self, glob):
        'Return the short refs of tags in the passed namespace'
        '%(refname:short): %(objectname:short)',
        fmt = '%(refname:short)'
        self.fetch()
        retcode, (out, err) = self.run(['for-each-ref', '--format', fmt, glob])
        return out

    def cat_file(self, ref):
        'Call cat-file -p on the ref passed'
        retcode, (out, err) = self.run(['cat-file', '-p', ref])
        return out

    def tag_dict(self, tag):
        'Return the contents of a tag as a dictionary'
        contents = self.cat_file(tag)
        split_contents = contents[3].split(' ')
        tagger, email, time, timezone = tagger_line_tokens(split_contents)
        body = yaml.load('\n'.join(contents[4:]))
        return {
            'tag': tag,
            'tagger_name': tagger,
            'tagger_email': email.strip('<>'),
            'time': time,
            'timezone': timezone,
            'body': body
        }

    def _recurse_tree(self, root, remaining):
        if not len(remaining):
            return root
        for _, git_type, oid, name in map(string.split, self.cat_file(root)):
            if name == remaining[0]:
                return self._recurse_tree(oid, remaining[1:])
        raise NoTree()

    def path_tree(self, path):
        'Get the object ID for the directory at `path`'
        root = self.cat_file('HEAD')[0].split()[1]
        try:
            return self._recurse_tree(root, path.split('/'))
        except NoTree:
            raise NoTree("No tree found for path: {0}".format(path))

    def checkout(self, commitish=None):
        'Check out the commitish'
        if not commitish:
            commitish = self.start_branch
        retcode, (out, err) = self.run(['checkout', commitish])
        if retcode > 0:
            raise CheckoutError(commitish)

    def show_note(self, ref_name):
        'Show notes for a release'
        self.checkout(ref_name)
        cmd = ['notes', '--ref', NS, 'show']
        _, (note, _) = self.run(cmd)
        self.checkout()
        return yaml.load('\n'.join(note))
