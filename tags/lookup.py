import os
from . import git


class HistoricRelease(object):
    'Convenience for looking at a release'

    note = None

    def __init__(self, repo, channel, number):
        self.channel = channel
        self.number = number
        ref_name = git.release_tag(channel, number)
        self.data = repo.tag_dict(ref_name)
        note = repo.show_note(ref_name)
        if note:
            self.note = note[channel][number]
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

    def packages(self, ref=None):
        'Get a list of packages defined at the passed commit'
        if not ref:
            ref = self.repo.start_branch
        self.repo.checkout(ref)
        ret_dict = {}
        not_git = filter(lambda path: '.git' not in path,
                         os.listdir(self.repo.root))
        for top_entry in not_git:
            for path, _, files in os.walk(os.path.join(self.repo.root, top_entry)):
                if '.package' in files:
                    if any([path.startswith(seen) for seen in ret_dict.keys()]):
                        msg = "Nested packages not allowed: {0}"
                        raise Exception(msg.format(path))
                    rel_path = os.path.relpath(path, self.repo.root)
                    ret_dict[rel_path] = self.repo.path_tree(rel_path)
        self.repo.checkout(self.repo.start_branch)
        return ret_dict

    def latest(self):
        refs = self._refs()
        if not refs:
            return None
        number, ref = refs[0]
        return HistoricRelease(self.repo, self.channel, number)

    def release(self, number):
        'Return the release for this channel at the number specified'
        return HistoricRelease(self.repo, self.channel, number)
