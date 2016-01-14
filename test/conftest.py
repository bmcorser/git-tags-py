# coding: utf-8
import pytest

import collections
import copy
import os
import tempfile
import traceback
import shutil
import uuid

from tags import git
from tags.release import Release


@pytest.fixture(scope='session')
def utils():
    utils_dict = {
        'result_tb': lambda result: traceback.print_tb(result.exc_info[2])
    }
    return collections.namedtuple('utils', utils_dict.keys())(**utils_dict)


def clone_from(root_dir, remote, local_name, user_name, user_email):
    'Create a clone from the specified remote, and set up user'
    local = os.path.join(root_dir, local_name)
    os.mkdir(local)
    git.run(root_dir, ['clone', remote, local])
    git.run(local, ['config', 'user.name', user_name])
    git.run(local, ['config', 'user.email', user_email])
    return local


def create_temp_repo():
    root_dir = tempfile.mkdtemp()
    # set up remote
    remote = os.path.join(root_dir, 'remote_repo')
    os.mkdir(remote)
    git.run(remote, ['init', '--bare'])

    # default local user
    user_name = 'Tarquin Tagger'
    user_email = 'tarquin@tagger.com'

    # tarquin's repo
    local = clone_from(root_dir, remote, 'local_repo', user_name, user_email)

    # tony's repo
    local_other = clone_from(
        root_dir, remote, 'local_repo_other', 'Tony Tagger', 'tony@tagger.com')

    # set up time-related things
    global time
    time = 1329000000

    def incr_time():
        'Increment the time that Git knows about'
        global time
        time += 100
        os.environ.update({
            'GIT_COMMITTER_DATE': "{0} +0000".format(time),
            'GIT_AUTHOR_DATE': "{0} +0000".format(time),
        })

    def touch(path):
        'Make a change to a file that Git will see'
        with open(os.path.join(local, path), 'w') as package_marker:
            package_marker.write(repr(uuid.uuid4().hex))

    def commit(name):
        'Touch the package marker file in the named directory and commit it'
        path = os.path.join(local, name, '.package')
        try:
            os.mkdir(os.path.join(local, name))
        except OSError as exc:
            if exc.errno != 17:
                raise
        touch(path)
        git.run(local, ['add', name])
        _, (out, _) = git.run(local, ['commit', '-m', name], env=incr_time())
        return out[0].split()[1].strip(']'), copy.copy(time)

    # make a commit that doesn’t create a package
    touch('initial-commit')
    git.run(local, ['add', '.'])
    git.run(local, ['commit', '-m', 'Initial commit'])
    git.run(local, ['push', 'origin', 'master'])

    git.run(local_other, ['pull'])

    def packages(*names):
        return [commit(name) for name in names]

    def cleanup():
        shutil.rmtree(root_dir)

    repo_dict = {
        'user_name': user_name,
        'user_email': user_email,
        'commit': commit,
        'packages': packages,
        'touch': touch,
        'root': root_dir,
        'local': local,
        'local_other': local_other,
        'remote': remote,
        'cleanup': cleanup,
        'incr_time': incr_time,
        'time': time,
    }
    return collections.namedtuple('repo', repo_dict.keys())(**repo_dict)


@pytest.yield_fixture(scope='function')
def fn_repo(request):
    repo_fs = create_temp_repo()
    yield repo_fs
    repo_fs.cleanup()


@pytest.fixture(scope='function')
def repo(fn_repo):
    return git.Repo(fn_repo.local)


@pytest.fixture(scope='function')
def release(repo):
    release_inst = Release(repo, 'test')
    release_inst.create_tag()
    return release_inst
