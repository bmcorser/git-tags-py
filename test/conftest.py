import pytest

import collections
import os
import tempfile
import traceback
import shutil
import subprocess


@pytest.fixture(scope='session')
def utils():
    utils_dict = {
        'result_tb': lambda result: traceback.print_tb(result.exc_info[2])
    }
    return collections.namedtuple('utils', utils_dict.keys())(**utils_dict)


def create_temp_repo():
    repo_dir = tempfile.mkdtemp()
    os.chdir(repo_dir)
    os.mkdir('remote_repo')
    os.chdir('remote_repo')
    subprocess.check_call(['git', 'init'])
    global time
    time = 1329828782
    def new_time():
        global time
        time += 100
        os.environ['GIT_COMMITTER_DATE'] = "{0} +0000".format(time)
        os.environ['GIT_AUTHOR_DATE'] = "{0} +0000".format(time)
    def touch(path):
        new_time()
        with open(path, 'w') as deploy_file:
            deploy_file.write(str(time))
    def commit(name):
        'Touch the deploy file in the named package and commit it'
        path = os.path.join(name, 'deploy')
        try:
            os.mkdir(name)
            os.mknod(path)
        except OSError as exc:
            if exc.errno != 17:
                raise
        touch(path)
        subprocess.check_call(['git', 'add', name])
        subprocess.check_call(['git', 'commit', '-m', name])
    def packages(*names):
        for name in names:
            commit(name)
    os.mknod('init')
    subprocess.check_call(['git', 'add', '.'])
    new_time()
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    '''subprocess.check_call(['git', 'tag', '-a', 'a', '-m', 'Tag a'])'''
    os.chdir(repo_dir)
    subprocess.check_call(['git', 'clone', 'remote_repo', 'local_repo'])
    os.chdir('local_repo')
    repo_dict = {
        'commit': commit,
        'packages': packages,
        'touch': touch,
        'dir': repo_dir,
    }
    return collections.namedtuple('repo', repo_dict.keys())(**repo_dict)


@pytest.yield_fixture(scope='function')
def function_repo():
    repo = create_temp_repo()
    yield repo
    shutil.rmtree(repo.dir)


@pytest.yield_fixture(scope='session')
def session_repo():
    repo = create_temp_repo()
    yield repo
    shutil.rmtree(repo)
