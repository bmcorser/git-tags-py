import os
import collections
import yaml
from . import git


class ReleaseLookupException(Exception):
    pass

class PackageNotFound(ReleaseLookupException):
    pass

class CommitNotFound(ReleaseLookupException):
    pass

class AliasNotFound(ReleaseLookupException):
    pass


def channel_releases(channel):
    'Get data for the last release'
    refs = git.channel_refs(channel)
    if not len(refs):
        return None
    refs.sort(reverse=True, key=lambda ref: int(ref.split('/')[-1]))
    return refs


def packages(repo_path):
    'Get a list of packages defined in the passed repository'
    ret_dict = {}
    not_git = filter(lambda path: '.git' not in path, os.listdir(repo_path))
    for path_ in not_git:
        for path, _, _ in os.walk(path_):
            attrs = git.attrs_dict(path)
            if attrs.pop('package', None) == 'set':
                if any([path.startswith(seen) for seen in ret_dict.keys()]):
                    msg = "Nested packages not allowed: {0}"
                    raise Exception(msg.format(path))
                ret_dict[os.path.relpath(path)] = attrs
    return ret_dict


def channel_latest(channel):
    refs = channel_releases(channel)

    def look_back(name):
        'Iterate through historic releases until we find our package'
        for ref in refs:
            tree = git.tag_dict(ref)['body'].get(name)
            if tree:
                return tree
    git.checkout(refs[0])
    ret_dict = {}
    previous_release = git.tag_dict(refs[0])['body']
    for name, attrs in packages('.').items():
        if name not in previous_release:
            tree = look_back(name)
        else:
            tree = previous_release[name]
        ret_dict[name] = tree
    return ret_dict

def channel_release(channel, number):
    ref = "releases/{0}/{1}".format(channel, number)
    git.checkout(ref)
    release = git.tag_dict(ref)
    global _refs
    _refs = None
    def look_back(name):
        'Iterate through historic releases until we find our package'
        global _refs
        if not _refs:
            _refs = channel_releases(channel)
        for ref in _refs:
            tree = git.tag_dict(ref)['body'].get(name)
            if tree:
                return tree
    ret_dict = {}
    for name, attrs in packages('.').items():
        if name not in release:
            tree = look_back(name)
        else:
            tree = release[name]
        ret_dict[name] = tree
    return ret_dict
