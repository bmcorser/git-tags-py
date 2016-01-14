import copy
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


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return result



class RepoError(Exception):
    'That is no repo'
    pass


class NoTree(RepoError):
    'No tree object found in the repo'
    pass


class CreateTagError(RepoError):
    'Could not create tag'
    pass


class CheckoutError(RepoError):
    'Some sort of error checking out a commit'
    pass


class FetchError(RepoError):
    'Could not fetch for some reason'
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
    repo.fetch_notes()
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


def run(directory, git_subcommand, return_proc=False, **popen_kwargs):
    '''
    Start a process to run the passed git subcommand in the passed directory
    Returns the return code and formatted output in a tuple nest like this:

        (returncode, (out, err))

    '''
    default_kwargs = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'cwd': directory,
    }
    default_kwargs.update(popen_kwargs)
    proc = subprocess.Popen(['git'] + git_subcommand,
                            **default_kwargs)
    if return_proc:
        return proc
    retcode = proc.wait()
    out, err = proc.communicate()
    if os.environ.get('DEBUG_GIT_STATE'):
        print('v'*80)
        print(' '.join(git_subcommand))
        print("out: {0}".format(out))
        print("err: {0}".format(err))
        print('^'*80)
    return retcode, map(utils.filter_empty_lines, (out, err))


def checked_out(directory, **popen_kwargs):
    'What branch is checked out in the passed directory'
    branch_cmd = ['symbolic-ref', '--quiet', 'HEAD']
    tag_cmd = ['describe', '--tags', '--exact-match']
    commit_cmd = ['rev-parse', 'HEAD']
    retcode, (out, err) = run(directory, branch_cmd, **popen_kwargs)
    if retcode == 0:  # branch found
        return out[0].replace('refs/heads/', '')
    retcode, (out, err) = run(directory, tag_cmd, **popen_kwargs)
    if retcode == 0:  # tag found
        return out[0]
    retcode, (out, err) = run(directory, commit_cmd, **popen_kwargs)
    if retcode == 0:  # not on a branch or tag
        return out[0]
    raise CheckoutError('Could not even rev-parse HEAD')


def repo_root(directory):
    'Look for the root of the closest git repo'
    root_cmd = ['rev-parse', '--show-toplevel']
    retcode, (out, err) = run(directory, root_cmd)
    if retcode > 0:
        raise RepoError('Not a repo?')
    return out[0]


class Repo(object):

    def __init__(self, directory, uid=None, gid=None):
        self.popen_kwargs = {}
        if uid and gid:
            self.popen_kwargs['preexec_fn'] = demote(uid, gid)
        self.root = repo_root(directory)
        self.start = checked_out(directory, **self.popen_kwargs)

    def run(self, cmd, **popen_kwargs):
        'Run a git command in this repo, just closes self.root'
        kwargs = copy.deepcopy(self.popen_kwargs)
        kwargs.update(popen_kwargs)
        return run(self.root, cmd, **kwargs)

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

    def fetch(self, refspec=None):
        'Fetch tags and commits, optionally to a refspec'
        if not self.has_remote():
            return 0, ([], [])
        # TODO: Find out what the remote is (not always origin)
        cmd = ['fetch', 'origin', '--tags']
        if refspec:
            cmd.append(refspec)
        retcode, (out, err) = self.run(cmd)
        if retcode > 0:
            raise FetchError('\n'.join(err))

    def fetch_notes(self):
        'Fetch notes'
        if not self.has_remote():
            return 0, ([], [])
        notes_ref = REF_NS.format(kind='notes', name='*')
        self.fetch("{0}:{0}".format(notes_ref))

    def create_tag(self, message, name):
        'Create a tag with the passed name and message (default user)'
        retcode, (out, err) = self.run(['tag', '-a', name, '-m', message])
        if retcode > 0:
            if 'unable to resolve ref' in err or 'still refs under' in err:
                click.echo('Did you use a package name as an alias?')
                raise CreateTagError(name)
            else:
                click.echo('\n'.join(err))
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
                for line in err:
                    click.echo(line)

    def push_ref(self, ref):
        'Push local tags to the remote'
        if not self.has_remote():
            return True, None
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
        retcode, (out, err) = self.run(['for-each-ref', '--format', fmt, glob])
        return out

    def cat_file(self, ref):
        'Call cat-file -p on the ref passed'
        retcode, (out, err) = self.run(['cat-file', '-p', ref])
        return out

    def tag_dict(self, tag):
        'Return the contents of a tag as a dictionary'
        contents = self.cat_file(tag)
        if not contents:
            return None
        split_contents = contents[3].split(' ')
        tagger, email, time, timezone = tagger_line_tokens(split_contents)
        body = yaml.load('\n'.join(contents[4:]))
        return {
            'tag': tag,
            'tagger_name': tagger,
            'tagger_email': email.strip('<>'),
            'time': "{0} {1}".format(time, timezone),
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
        if path == '/':
            return root
        try:
            return self._recurse_tree(root, path.split('/'))
        except NoTree:
            raise NoTree("No tree found for path: {0}".format(path))

    def checkout(self, commitish=None):
        'Check out the commitish'
        if not commitish:
            commitish = self.start
        cmd = ['checkout', commitish]
        if os.environ.get('GIT_TAGS_FORCE_CHECKOUT'):
            cmd.append('-qf')
        retcode, (out, err) = self.run(cmd)
        if retcode > 0:
            raise CheckoutError("({0}) {1}".format(commitish, '\n'.join(err)))

    def show_note(self, ref_name):
        'Show notes for a release'
        self.checkout(ref_name)
        cmd = ['notes', '--ref', NS, 'show']
        _, (note, _) = self.run(cmd)
        if not note:
            try:
                self.fetch_notes()
                _, (note, _) = self.run(cmd)
            except FetchError as exc:
                # don't leave the user somewhere different
                self.checkout()
        self.checkout()
        return yaml.load('\n'.join(note))

    def packages(self, ref=None):
        'Get a list of packages defined at the passed commit'
        self.checkout(ref)
        repo_files = self.run(['ls-files'], return_proc=True)
        grep_cmd = ['grep', '\.package']
        grep_proc = subprocess.Popen(grep_cmd,
                                     stdin=repo_files.stdout,
                                     stdout=subprocess.PIPE)
        package_markers, err = grep_proc.communicate()
        ret_dict = {}
        for path in package_markers.split():
            if path == '.package':  # root package
                ret_dict['/'] = self.path_tree('/')
                continue  # to check raise in case of nesting
            if path.endswith('.package'):
                if any([path.startswith(seen) for seen in ret_dict.keys()]):
                    msg = "Nested packages not allowed: {0}"
                    raise Exception(msg.format(path))
                directory, filename = os.path.split(path)
                ret_dict[directory] = self.path_tree(directory)
        self.checkout()
        return ret_dict
