from . import git


def sort_releases(releases):
    'Return sorted list of release tags (by commit time, not tag time)'
    get_commit = lambda tag: tag.split('/')[-1]
    commit_releases = {get_commit(tag): tag for tag in releases}
    sorted_commits = git.sort_refs(commit_releases.keys())
    return [commit_releases[commit_] for commit_ in sorted_commits]


def commit(name, _alias=None):
    'Return data for packages released at passed commit, filtered by alias'
    glob = git.fmt_tag(alias=_alias, pkg='*', commit=name)
    commit_tags = git.tag_refs(glob)
    return map(git.tag_dict, sort_releases(commit_tags))


def package(name, _alias=None):
    '''
    Return number (default one) of historic releases for passed package and
    optional alias.
    '''
    glob = git.fmt_tag(alias=_alias, pkg=name, commit='*')
    pkg_tags = git.tag_refs(glob)
    return map(git.tag_dict, sort_releases(pkg_tags))


def alias_pkgs(name):
    'Return packages included in passed alias'
    glob = git.fmt_tag(alias=name, pkg='*', commit='*')
    alias_tags = git.tag_refs(glob)
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
