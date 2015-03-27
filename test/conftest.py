import pytest

import os
import tempfile
import shutil
import subprocess


def create_temp_repo():
    repo_dir = tempfile.mkdtemp()
    os.chdir(repo_dir)
    os.mkdir('remote_repo')
    os.chdir('remote_repo')
    subprocess.check_call(['git', 'init'])
    os.mkdir('a')
    os.mknod('a/deploy')
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    subprocess.check_call(['git', 'tag', '-a', 'a', '-m', 'Tag a'])
    os.mkdir('b')
    os.mknod('b/deploy')
    subprocess.check_call(['git', 'add', '.'])
    subprocess.check_call(['git', 'commit', '-m', 'Second commit'])
    subprocess.check_call(['git', 'tag', '-a', 'b', '-m', 'Tag b'])
    os.chdir(repo_dir)
    subprocess.check_call(['git', 'clone', 'remote_repo', 'local_repo'])
    os.chdir('local_repo')
    return repo_dir


@pytest.yield_fixture(scope='function')
def function_repo():
    repo = create_temp_repo()
    yield repo
    shutil.rmtree(repo)


@pytest.yield_fixture(scope='session')
def session_repo():
    repo = create_temp_repo()
    yield repo
    shutil.rmtree(repo)
