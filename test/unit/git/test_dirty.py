def test_dirty_clean(repo):
    'Dirty returns False when the repo is clean'
    assert bool(repo.status()) == False


def test_dirty_untracked(fn_repo, repo):
    'Dirty returns True when there are untracked files'
    fn_repo.touch('c')
    assert bool(repo.status()) == True


def test_dirty_unstaged(fn_repo, repo):
    'Dirty returns True when there are unstaged files'
    fn_repo.touch('c')
    repo.run(['add', 'c'])
    repo.run(['commit', '-m', 'abxc'])
    fn_repo.touch('c')
    assert bool(repo.status()) == True


def test_dirty_uncommitted(fn_repo, repo):
    'Dirty returns True when there are unstaged files'
    fn_repo.touch('c')
    repo.run(['add', 'c'])
    assert bool(repo.status()) == True
