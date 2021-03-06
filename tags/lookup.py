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
        note = repo.show_note(ref_name)
        if not note:
            repo.fetch_notes()
            note = repo.show_note(ref_name)
        try:
            msg = 'No release notes for {0}'
            self.note = note[channel][number]
        except KeyError:
            repo.fetch_notes()
            try:
                self.note = repo.show_note(ref_name)[channel][number]
            except KeyError:
                raise NotesMissing(msg.format(ref_name))
        except TypeError:
            raise NotesMissing(msg.format(ref_name))
        self.ref_name = ref_name

    def json(self):
        'Render JSON'
        ret = {}
        for name in ['channel', 'number', 'ref_name', 'note', 'data']:
            ret[name] = getattr(self, name)
        return ret


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
            # second chance
            self.repo.fetch()
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

    def latest(self):
        self.repo.fetch()
        self.repo.fetch_notes()
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
