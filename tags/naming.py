import functools


def format_tag(commit, alias, pkg):
    if alias:
        return "{0}/{1}/{2}".format(pkg, commit, alias)
    else:
        return "{0}/{1}".format(pkg, commit)


def format_tags(pkgs, commit, alias):
    return map(functools.partial(format_tag, commit, alias), pkgs)
