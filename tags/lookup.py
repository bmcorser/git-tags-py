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
    refs.sort(reverse=True)
    return [ref.split(': ')[0] for ref in refs]


def sort_releases(releases):
    'Return sorted list of release tags (by commit time, not tag time)'
    get_commit = lambda tag: tag.split('/')[-1]  # probably not quicker to
                                                 # subprocess to cat-file
    commit_releases = collections.defaultdict(set)
    for tag in releases:
        commit_releases[get_commit(tag)].add(tag)
    sorted_commits = git.sort_refs(commit_releases.keys())
    sorted_tags = []
    for commit_ in sorted_commits:
        sorted_tags.extend(sorted(commit_releases.get(commit_)))
    return sorted_tags


def commit(name, _alias=None):
    'Return data for packages released at passed commit, filtered by alias'
    glob = git.fmt_tag(alias=_alias, pkg='**', commit=name)
    commit_tags = git.tag_refs(glob)
    if not commit_tags:
        raise CommitNotFound("No releases for commit {0}".format(name))
    return map(git.tag_dict, sort_releases(commit_tags))


def package(name, _alias=None):
    '''
    Return number (default one) of historic releases for passed package and
    optional alias.
    '''
    glob = git.fmt_tag(alias=_alias, pkg=name, commit='**')
    pkg_tags = git.tag_refs(glob)
    if not pkg_tags:
        raise PackageNotFound("No releases for package {0}".format(name))
    return map(git.tag_dict, sort_releases(pkg_tags))


def alias_pkgs(name):
    'Return packages included in passed alias'
    glob = git.fmt_tag(alias=name, pkg='*', commit='*')
    alias_tags = git.tag_refs(glob)
    if not alias_tags:
        raise AliasNotFound("No releases under alias {0}".format(name))
    pkgs = set()
    for tag in alias_tags:
        _, _, pkg, _ = tag.split('/')
        pkgs.add(pkg)
    return pkgs


def alias(name):
    'Return release data for passed alias'
    pkgs = alias_pkgs(name)
    alias_tags = {}
    for pkg in pkgs:
        alias_tags[pkg] = package(pkg, _alias=name)
    return alias_tags
