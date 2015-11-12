import os
import subprocess
import arrow
from . import git


class LookupError(Exception):
    'That is no repo'
    pass


class NotesMissing(LookupError):
    'Release notes are missing'
    pass


class NoTag(LookupError):
    'Release notes are missing'
    pass


class HistoricRelease(object):
    'Convenience for looking at a release'

    note = None

    def __init__(self, repo, channel, number):
        if not isinstance(number, int):
            msg = "Release number is not an integer: {0}"
            raise LookupError(msg.format(type(number)))
        self.channel = channel
        self.number = number
        ref_name = git.release_tag(channel, number)
        self.data = repo.tag_dict(ref_name)
        if not self.data:
            msg = "'{0}' does not refer to a known release"
            raise NoTag(msg.format(ref_name))
        self.time = arrow.get(self.data['time'], "X Z")
        repo.fetch_notes()
        note = repo.show_note(ref_name)
        try:
            self.note = note[channel][number]
        except KeyError:
            msg = 'No release notes for {0}'
            raise NotesMissing(msg.format(ref_name))
        self.ref_name = ref_name


class Lookup(object):
    '''
    Do release lookups for in the passed repository and channel, leaving that
    repo at `head` when done
    '''

    def __init__(self, repo, channel):
        self.repo = repo
        self.channel = channel

    def _refs(self):
        '''
        Return a sorted list of number and ref for releases in this channel,
        latest first
        '''
        glob = git.release_ref(self.channel)
        refs = self.repo.refs_glob(glob)
        if not len(refs):
            return None
        return sorted([(git.release_number(ref), ref) for ref in refs],
                      reverse=True,
                      key=lambda T: T[0])

    def listing(self):
        'List all the releases on this channel'
        return [HistoricRelease(self.repo, self.channel, number)
                for number, _ in self._refs()]

    def packages(self, ref=None):
        'Get a list of packages defined at the passed commit'
        if not ref:
            ref = self.repo.start_branch
        self.repo.checkout(ref)
        repo_files = self.repo.run(['ls-files'], return_proc=True)
        grep_cmd = ['grep', '\.package']
        grep_proc = subprocess.Popen(grep_cmd,
                                     stdin=repo_files.stdout,
                                     stdout=subprocess.PIPE)
        package_markers, err = grep_proc.communicate()
        ret_dict = {}
        for path in package_markers.split():
            if path == '.package':  # root package
                ret_dict['/'] = self.repo.path_tree('/')
                continue  # to check raise in case of nesting
            if path.endswith('.package'):
                if any([path.startswith(seen) for seen in ret_dict.keys()]):
                    msg = "Nested packages not allowed: {0}"
                    raise Exception(msg.format(path))
                directory, filename = os.path.split(path)
                ret_dict[directory] = self.repo.path_tree(directory)
        self.repo.checkout()
        return ret_dict

    def latest(self):
        refs = self._refs()
        if not refs:
            return None
        number, ref = refs[0]
        return HistoricRelease(self.repo, self.channel, number)

    def release(self, number):
        'Return the release for this channel at the number specified'
        try:
            return HistoricRelease(self.repo, self.channel, number)
        except:  # TODO: Exception types
            self.repo.fetch()
            self.repo.fetch_notes()
            return HistoricRelease(self.repo, self.channel, number)
