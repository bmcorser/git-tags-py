import functools


def format_tag(commit, alias, pkg):
    if alias:
        return "{0}/{1}/{2}".format(commit, pkg, alias)
    else:
        return "{0}/{1}".format(commit, pkg)


def format_tags(pkgs, commit, alias):
    return map(functools.partial(format_tag, commit, alias), pkgs)
