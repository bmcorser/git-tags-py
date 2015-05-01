import random
from tags import git, lookup


def test_lookup_sort_releases(function_repo):
    'Correctly sorts tags by referenced commit'
    pkg = 'a'
    commit_time = function_repo.packages(*(pkg,) * 5)
    commits = [commit for commit, _ in commit_time]
    tags = [git.fmt_tag(pkg, commit, None) for commit in reversed(commits)]
    for tag in tags:
        function_repo.inc_time()
        git.create_tag('...', tag)
    # shuffle tags before sort
    shuffled_tags = random.sample(tags, len(tags))
    # when sorted should be the reverse of commit order
    expected = list(tags)
    '''
    DAG:           o <-- o <-- o <-- o <-- o
    Commit time:   0     1     2     3     4
    Tag time:      4     3     2     1     0
    Sorted:        4     3     2     1     0
    '''
    assert lookup.sort_releases(shuffled_tags) == expected


def test_lookup_sort_releases_alias(function_repo):
    '''
    Correctly sorts tags by referenced commit, duplicate commits are sorted
    lexographically (or whatever the default is for `sorted`)
    '''
    pkg = 'a'
    alias = 'z'
    commit_time = function_repo.packages(*(pkg,) * 5)
    commits = [commit for commit, _ in commit_time]
    tags = [git.fmt_tag(pkg, commit, None) for commit in reversed(commits)]
    alias_tags = [git.fmt_tag(pkg, commit, alias)
                  for commit in reversed(commits)]
    all_tags = tags + alias_tags
    for tag in all_tags:
        function_repo.inc_time()
        git.create_tag('...', tag)
    shuffled_tags = random.sample(all_tags, len(all_tags))
    expected = []
    for idx, tag in enumerate(tags):
        expected.append(tag)
        expected.append(alias_tags[idx])
    assert lookup.sort_releases(shuffled_tags) == expected
