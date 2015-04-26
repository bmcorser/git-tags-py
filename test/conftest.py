import pytest

import collections
import copy
import operator
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
    old_dir = os.getcwd()
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
        new_time()
        commit_return = subprocess.check_output(['git', 'commit', '-m', name])
        return commit_return.split(' ')[1].strip(']'), copy.copy(time)
    def packages(*names):
        return [commit(name) for name in names]
    os.mknod('init')
    subprocess.check_call(['git', 'add', '.'])
    new_time()
    subprocess.check_call(['git', 'commit', '-m', 'Initial commit'])
    '''subprocess.check_call(['git', 'tag', '-a', 'a', '-m', 'Tag a'])'''
    os.chdir(repo_dir)
    subprocess.check_call(['git', 'clone', 'remote_repo', 'local_repo'])
    os.chdir('local_repo')
    user_name = 'Tarquin Tagger'
    user_email = 'tarquin@tagger.com'
    subprocess.check_output(['git', 'config', 'user.name', user_name])
    subprocess.check_output(['git', 'config', 'user.email', user_email])
    def cleanup():
        os.chdir(old_dir)
        shutil.rmtree(repo_dir)
    repo_dict = {
        'user_name': user_name,
        'user_email': user_email,
        'commit': commit,
        'packages': packages,
        'touch': touch,
        'dir': repo_dir,
        'cleanup': cleanup,
    }
    return collections.namedtuple('repo', repo_dict.keys())(**repo_dict)


@pytest.yield_fixture(scope='function')
def function_repo(request):
    repo = create_temp_repo()
    yield repo
    repo.cleanup()
