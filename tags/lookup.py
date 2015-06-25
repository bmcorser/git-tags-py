import os
from . import git


class Lookup(object):
    '''
    Do release lookups for in the passed repository and channel, leaving that
    repo at `head` when done
    '''

    def __init__(self, repo_root, head, channel):
        self.repo_root = repo_root
        self.head = head
        self.channel = channel

    def releases(self):
        'Return a sorted list of releases in this channel, latest first'
        glob = git.release_ref(self.channel)
        refs = git.refs_glob(glob)
        if not len(refs):
            return None
        refs.sort(reverse=True, key=lambda ref: int(ref.split('/')[-1]))
        return refs

    def packages(self, ref):
        'Get a list of packages defined at the passed commit'
        git.checkout(ref)
        ret_dict = {}
        not_git = filter(lambda path: '.git' not in path,
                         os.listdir(self.repo_root))
        for top_entry in not_git:
            for path, _, files in os.walk(top_entry):
                if '.package' in files:
                    if any([path.startswith(seen) for seen in ret_dict.keys()]):
                        msg = "Nested packages not allowed: {0}"
                        raise Exception(msg.format(path))
                    rel_path = os.path.relpath(path)
                    ret_dict[rel_path] = git.path_tree(rel_path)
        git.checkout(self.head)
        return ret_dict

    def latest(self):
        refs = self.releases()
        if not refs:
            return None
        return git.tag_dict(refs[0])

    def release(self, number):
        'Return the release for this channel at the number specified'
        ref = git.release_tag(self.channel, number)
        release_dict = git.tag_dict(ref)
        return release_dict
