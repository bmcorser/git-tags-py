import pytest

import os
import tempfile

import pygit2


@pytest.fixture(scope='session')
def session_repo(request):
    tempdir = tempfile.mkdtemp()
    os.chdir(tempdir)

    repo = pygit2.init_repository(tempdir)
    repo.config['user.name'] = 'Timmy Testman'
    repo.config['user.email'] = 'timmy@testman.com'
    user = pygit2.Signature(repo.config['user.name'], repo.config['user.email'])

    master = 'refs/heads/master'

    os.mkdir('a')
    os.mknod('a/a')
    repo.index.add_all(['a'])
    tree = repo.TreeBuilder().write()
    initial = repo.create_commit(master, user, user, 'Inital commit', tree, [])
    repo.create_tag('a', initial.hex, pygit2.GIT_OBJ_COMMIT, user, 'Tag a')

    os.mkdir('b')
    os.mknod('b/a')
    repo.index.add_all(['b'])
    tree = repo.TreeBuilder().write()
    repo.create_commit(master, user, user, 'Second commit', tree, [initial])
    repo.create_tag('b', repo.revparse_single('HEAD').hex,
                    pygit2.GIT_OBJ_COMMIT, user, 'Tag b')
    return repo

@pytest.fixture
def run_git_tests(session_repo):
    def run_git_tests_fn(git):

        # test get_head_sha1
        retval = git.get_head_sha1()
        assert retval == session_repo.revparse_single('HEAD').hex

        # test get_tag_list
        retval = git.get_tag_list()
        assert retval == ['a', 'b']

    return run_git_tests_fn
